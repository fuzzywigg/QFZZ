# Operations & Maintenance Guide

Complete guide for operating and maintaining QFZZ in production.

## Overview

This guide covers day-to-day operations, monitoring, backups, and troubleshooting for QFZZ.

## Health Monitoring

### Health Check API

QFZZ provides built-in health checks:

```python
from qfzz.utils.health import health_check

# Get health status
status = health_check()

print(f"Status: {status.status}")  # healthy, degraded, or unhealthy
print(f"Uptime: {status.uptime_seconds}s")
print(f"Version: {status.version}")

# Check specific components
for name, check in status.checks.items():
    print(f"{name}: {check['status']}")
```

### CLI Health Check

```bash
# Run health check
python -m qfzz.utils.health

# Exit codes:
# 0 = healthy
# 1 = degraded
# 2 = unhealthy
```

### Monitored Components

- **Disk Space**: Warns if < 1GB free
- **Memory**: Warns if > 90% used
- **CPU**: Warns if > 90% used
- **Ledger**: Validates file exists and is valid JSON
- **Knowledge Graph**: Checks file existence
- **Audio Content**: Checks directory exists

### Integration with Monitoring

#### Prometheus

Add to scrape config:
```yaml
scrape_configs:
  - job_name: 'qfzz'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['localhost:8001']
```

#### Nagios/Icinga

```bash
#!/bin/bash
# check_qfzz_health.sh
python -m qfzz.utils.health > /dev/null
exit $?
```

## Backup & Restore

### Automated Backups

```bash
# Run backup
./scripts/backup.sh

# Include audio content
BACKUP_AUDIO=true ./scripts/backup.sh

# Custom backup location
BACKUP_DIR=/mnt/backups ./scripts/backup.sh

# Custom retention
RETENTION_DAYS=30 ./scripts/backup.sh
```

### What Gets Backed Up

**Always**:
- `qfzz_ledger.json` - Blockchain ledger
- `qfzz_knowledge_graph.json` - Knowledge graph
- `honeycomb/` - Application state
- `.env` - Configuration
- `config/` - Configuration files

**Optional** (set `BACKUP_AUDIO=true`):
- `qfzz_audio_content/` - Audio files

### Scheduled Backups

#### Cron

```bash
# Daily at 2 AM
0 2 * * * cd /opt/qfzz && ./scripts/backup.sh >> /var/log/qfzz-backup.log 2>&1

# Every 6 hours
0 */6 * * * cd /opt/qfzz && ./scripts/backup.sh >> /var/log/qfzz-backup.log 2>&1
```

#### Systemd Timer

Create `/etc/systemd/system/qfzz-backup.timer`:
```ini
[Unit]
Description=QFZZ Backup Timer

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

Create `/etc/systemd/system/qfzz-backup.service`:
```ini
[Unit]
Description=QFZZ Backup Service

[Service]
Type=oneshot
User=qfzz
WorkingDirectory=/opt/qfzz
ExecStart=/opt/qfzz/scripts/backup.sh
```

Enable:
```bash
sudo systemctl enable qfzz-backup.timer
sudo systemctl start qfzz-backup.timer
```

### Restore from Backup

```bash
# List available backups
./scripts/restore.sh

# Restore specific backup
./scripts/restore.sh 20260126_020000

# Verify after restore
python scripts/verify-ledger.py
```

### Off-site Backups

#### S3/Cloud Storage

```bash
#!/bin/bash
# sync-backups.sh

BACKUP_DIR=/opt/qfzz/backups
S3_BUCKET=s3://my-qfzz-backups

# Sync to S3
aws s3 sync "$BACKUP_DIR" "$S3_BUCKET" --exclude "*" --include "*.tar.gz"

# Or use rclone
rclone sync "$BACKUP_DIR" "remote:qfzz-backups"
```

#### Remote Server

```bash
#!/bin/bash
# rsync to remote server

BACKUP_DIR=/opt/qfzz/backups
REMOTE=backup@backup-server.example.com:/backups/qfzz/

rsync -avz --progress "$BACKUP_DIR/"*.tar.gz "$REMOTE"
```

## Log Management

### Log Locations

- Application logs: `logs/qfzz.log`
- Icecast logs: `logs/icecast/`
- Verification logs: `logs/ledger-verification.log`
- System logs: `journalctl -u qfzz`

### Log Rotation

Create `/etc/logrotate.d/qfzz`:
```
/opt/qfzz/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 qfzz qfzz
    sharedscripts
    postrotate
        systemctl reload qfzz 2>/dev/null || true
    endscript
}
```

### Viewing Logs

```bash
# Real-time logs
tail -f logs/qfzz.log

# Last 100 lines
tail -100 logs/qfzz.log

# Search logs
grep "ERROR" logs/qfzz.log

# Journal logs
journalctl -u qfzz -f
```

## Performance Monitoring

### System Metrics

```bash
# CPU and memory
htop

# Disk I/O
iotop

# Network
iftop

# All-in-one
glances
```

### Application Metrics

```python
from qfzz.utils.health import get_health_checker

checker = get_health_checker()

# CPU usage
cpu = checker.check_cpu()
print(f"CPU: {cpu['percent_used']}%")

# Memory usage
memory = checker.check_memory()
print(f"Memory: {memory['percent_used']}%")

# Disk space
disk = checker.check_disk_space()
print(f"Disk: {disk['free_gb']}GB free")
```

### Database Performance

```sql
-- PostgreSQL slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- Connection count
SELECT count(*) FROM pg_stat_activity;

-- Database size
SELECT pg_size_pretty(pg_database_size('qfzz'));
```

## Security

### Regular Security Audits

```bash
# Check for outdated packages
pip list --outdated

# Security vulnerability scan
pip-audit

# File permissions
find /opt/qfzz -type f -perm /go+w

# Check exposed ports
netstat -tlnp
```

### Update Dependencies

```bash
# Update Python packages
pip install --upgrade -r requirements.txt

# Update system packages
sudo apt-get update && sudo apt-get upgrade
```

### Secrets Management

```bash
# Encrypt .env file
gpg --symmetric --cipher-algo AES256 .env

# Decrypt
gpg --decrypt .env.gpg > .env

# Use environment variables instead
export GOOGLE_AI_API_KEY="your_key"
python run_server.py
```

## Troubleshooting

### High Memory Usage

```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head -10

# Restart service
sudo systemctl restart qfzz
```

### Disk Full

```bash
# Find large files
du -h / | sort -rh | head -20

# Clean old backups
find /opt/qfzz/backups -mtime +30 -delete

# Clean logs
truncate -s 0 /opt/qfzz/logs/*.log
```

### Service Won't Start

```bash
# Check logs
journalctl -u qfzz -n 50

# Check permissions
ls -la /opt/qfzz

# Test manually
cd /opt/qfzz
python run_server.py
```

### Database Connection Issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -U qfzz -d qfzz -c "SELECT 1;"

# Reset connections
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'qfzz' AND pid <> pg_backend_pid();
```

## Maintenance Tasks

### Weekly

- [ ] Review logs for errors
- [ ] Check backup success
- [ ] Verify disk space
- [ ] Review health checks

### Monthly

- [ ] Update dependencies
- [ ] Security audit
- [ ] Performance review
- [ ] Test restore from backup
- [ ] Clean old data

### Quarterly

- [ ] Major version updates
- [ ] Infrastructure review
- [ ] Disaster recovery test
- [ ] Documentation update

## Alerts

### Setup Email Alerts

```bash
#!/bin/bash
# alert.sh

SUBJECT="QFZZ Alert: $1"
BODY="$2"
TO="admin@example.com"

echo "$BODY" | mail -s "$SUBJECT" "$TO"
```

### Health Check Alerts

```bash
#!/bin/bash
# health-check-alert.sh

OUTPUT=$(python -m qfzz.utils.health 2>&1)
STATUS=$?

if [ $STATUS -ne 0 ]; then
    ./alert.sh "Health Check Failed" "$OUTPUT"
fi
```

### Disk Space Alerts

```bash
#!/bin/bash
# disk-alert.sh

THRESHOLD=90
USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')

if [ $USAGE -gt $THRESHOLD ]; then
    ./alert.sh "Disk Space Low" "Disk usage: ${USAGE}%"
fi
```

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
services:
  qfzz-app:
    deploy:
      replicas: 3
      
  nginx:
    image: nginx
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
```

### Vertical Scaling

```yaml
# Increase resources
services:
  qfzz-app:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
        reservations:
          cpus: '2'
          memory: 2G
```

### Database Scaling

```sql
-- Add read replicas
CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'password';

-- Optimize queries
CREATE INDEX idx_tracks_title ON tracks(title);
CREATE INDEX idx_playback_user_time ON playback_history(user_id, played_at);
```

## Disaster Recovery

### Recovery Plan

1. **Assess Damage**
   - What failed?
   - What data was lost?
   - When did it fail?

2. **Restore from Backup**
   ```bash
   ./scripts/restore.sh <latest_backup>
   ```

3. **Verify Integrity**
   ```bash
   python scripts/verify-ledger.py
   python -m qfzz.utils.health
   ```

4. **Restart Services**
   ```bash
   docker compose down
   docker compose up -d
   ```

5. **Monitor**
   - Watch logs
   - Check health
   - Verify functionality

### Testing Recovery

```bash
# 1. Create backup
./scripts/backup.sh

# 2. Stop services
docker compose down

# 3. Simulate data loss
rm qfzz_ledger.json

# 4. Restore
./scripts/restore.sh <backup_timestamp>

# 5. Verify
python scripts/verify-ledger.py

# 6. Restart
docker compose up -d
```

## Best Practices

### Operations

1. **Regular Backups**: Automated daily backups
2. **Monitoring**: 24/7 health checks
3. **Logging**: Centralized log aggregation
4. **Documentation**: Keep runbooks updated
5. **Testing**: Regular disaster recovery drills

### Security

1. **Least Privilege**: Minimal permissions
2. **Encryption**: Encrypt sensitive data
3. **Updates**: Regular security updates
4. **Auditing**: Regular security audits
5. **Secrets**: Never commit secrets

### Performance

1. **Monitoring**: Track all metrics
2. **Optimization**: Profile and optimize
3. **Caching**: Use Redis for caching
4. **Scaling**: Scale horizontally
5. **Database**: Optimize queries

## Resources

- **QFZZ Documentation**: Full docs in `docs/`
- **Docker Guide**: `docs/DOCKER_GUIDE.md`
- **Icecast Guide**: `docs/ICECAST_GUIDE.md`
- **Ledger Verification**: `docs/LEDGER_VERIFICATION.md`

## Support

For operational issues:
- Check logs first
- Review this guide
- Run health checks
- Test restore procedures
- Open GitHub issue if needed

---

**Remember**: Good operations is about preparation, monitoring, and quick response to issues.
