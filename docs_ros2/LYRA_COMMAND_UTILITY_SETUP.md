# LYRA ROBOT - COMMAND UTILITY SETUP GUIDE

## Quick Start (2 minutes)

### 1. Enable the Commands
```bash
# Add to your ~/.bashrc
echo "source ~/lyra_ws/lyra_commands.sh" >> ~/.bashrc

# Reload shell
source ~/.bashrc

# Verify it worked
lyra-help
```

### 2. Test It Works
```bash
# Quick hardware check (no robot needed)
lyra-test-connectivity

# If robot is running:
lyra-status
```

### 3. You're Done!
```bash
# Now use any lyra-* command:
lyra-launch-robot-teleop
lyra-arm
lyra-battery
# etc...
```

---

## Full Installation

### Step 1: Copy Files to Workspace
```bash
# Copy to your ROS workspace
cp lyra_commands.sh ~/lyra_ws/
cp lyra_doctor.sh ~/lyra_ws/
chmod +x ~/lyra_ws/lyra_commands.sh
chmod +x ~/lyra_ws/lyra_doctor.sh
```

### Step 2: Update Workspace Path (if needed)
If your workspace is NOT at `~/lyra_ws`:

**Edit lyra_commands.sh:**
```bash
# Find this line:
LYRA_WS="${HOME}/lyra_ws"

# Change to your actual workspace:
LYRA_WS="/path/to/your/workspace"
```

### Step 3: Add to Shell Profile
```bash
# Add to ~/.bashrc (for bash)
echo "source ~/lyra_ws/lyra_commands.sh" >> ~/.bashrc

# OR add to ~/.zshrc (for zsh)
echo "source ~/lyra_ws/lyra_commands.sh" >> ~/.zshrc

# OR add to ~/.fish/config.fish (for fish shell)
echo "source ~/lyra_ws/lyra_commands.sh" >> ~/.config/fish/config.fish
```

### Step 4: Reload Shell
```bash
source ~/.bashrc    # or ~/.zshrc or source ~/.config/fish/config.fish
```

### Step 5: Verify Setup
```bash
# This should work now:
lyra-help

# You should see:
# [LYRA] Lyra Robot Command Utility Loaded
# Type 'lyra-help' for available commands
```

---

## Using the Scripts

### Daily Use
```bash
# Source is automatic (done in ~/.bashrc)
# Just open a terminal and type:
lyra-launch-robot-teleop
lyra-arm
# No need to source anything!
```

### Manual Sourcing (if not in ~/.bashrc)
```bash
source ~/lyra_ws/lyra_commands.sh
lyra-help
```

### One-Off Commands
```bash
# If you don't want to source the whole file:
$(source ~/lyra_ws/lyra_commands.sh && lyra-arm)
```

---

## Troubleshooting Setup

### "command not found: lyra-*"
```bash
# Verify file exists
ls -la ~/lyra_ws/lyra_commands.sh

# Verify it's in your ~/.bashrc
grep "lyra_commands" ~/.bashrc

# If not there, add it:
echo "source ~/lyra_ws/lyra_commands.sh" >> ~/.bashrc

# Reload shell:
source ~/.bashrc
```

### "LYRA_WS not found"
```bash
# The script checks if workspace exists
# Verify workspace location:
ls -la ~/lyra_ws/

# If workspace is elsewhere, edit the script:
nano ~/lyra_ws/lyra_commands.sh

# Find and change:
LYRA_WS="${HOME}/lyra_ws"
# to:
LYRA_WS="/your/actual/path"
```

### "ROS not found"
```bash
# Your ROS setup is not sourced
# Make sure you have ROS sourced BEFORE running commands:
source /opt/ros/$ROS_DISTRO/setup.bash

# Add to ~/.bashrc to make it permanent:
echo "source /opt/ros/$(echo $ROS_DISTRO)/setup.bash" >> ~/.bashrc
```

---

## Advanced Setup

### Create Custom Aliases
Edit `~/.bashrc` and add:
```bash
# Fast shortcuts
alias ll='lyra-launch-robot-teleop'
alias ln='lyra-launch-robot-nav'
alias ls='lyra-launch-robot-slam'
alias la='lyra-arm'
alias ld='lyra-disarm'
alias lx='lyra-stop'
alias lh='lyra-help'

# Or use your own abbreviations:
alias launch-test='lyra-launch-bridge'
alias quick-status='lyra-status'
```

Then reload and use:
```bash
ll              # same as lyra-launch-robot-teleop
la              # same as lyra-arm
lx              # same as lyra-stop
```

### Create ROS Daemon Monitor
Add to `~/.bashrc`:
```bash
# Monitor ROS daemon at shell startup
function check_ros() {
    if ! ros2 daemon ping &>/dev/null 2>&1; then
        echo "⚠️  ROS daemon not running. Starting..."
        ros2 daemon start
    fi
}

# Run on shell startup (optional)
# check_ros
```

### Setup Automatic Sourcing on SSH
For remote SSH sessions, add to `~/.bashrc`:
```bash
# Auto-source on every login
if [ -f ~/lyra_ws/lyra_commands.sh ]; then
    source ~/lyra_ws/lyra_commands.sh
fi
```

---

## Doctor Script Setup

The `lyra_doctor.sh` script provides automated diagnostics and healing.

### Basic Usage
```bash
# Run diagnostic checks
./lyra_doctor.sh

# Run with verbose output
./lyra_doctor.sh --verbose

# Run and auto-fix issues found
./lyra_doctor.sh --fix
```

### Add to Startup
Create `~/run_doctor.sh`:
```bash
#!/bin/bash
cd ~/lyra_ws
./lyra_doctor.sh --verbose
```

Then make it executable:
```bash
chmod +x ~/run_doctor.sh
```

Run before important sessions:
```bash
~/run_doctor.sh
```

### Schedule Regular Checks
Add cron job to run diagnostics daily:
```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 9 AM):
0 9 * * * ~/lyra_ws/lyra_doctor.sh --verbose >> ~/logs/doctor.log 2>&1
```

---

## Integration with IDE/Tools

### VS Code Integration
Add to VS Code workspace settings (`.vscode/settings.json`):
```json
{
    "terminal.integrated.shellArgs.linux": ["--login"],
    "terminal.integrated.env.linux": {
        "ROS_DISTRO": "humble",
        "ROS_SETUP": "/opt/ros/humble/setup.bash"
    }
}
```

Add tasks to `.vscode/tasks.json`:
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Lyra: Launch Teleop",
            "type": "shell",
            "command": "source ~/lyra_ws/lyra_commands.sh && lyra-launch-robot-teleop",
            "isBackground": true
        },
        {
            "label": "Lyra: Launch SLAM",
            "type": "shell",
            "command": "source ~/lyra_ws/lyra_commands.sh && lyra-launch-robot-slam"
        },
        {
            "label": "Lyra: Doctor Check",
            "type": "shell",
            "command": "~/lyra_ws/lyra_doctor.sh --verbose"
        }
    ]
}
```

Then run from VS Code Command Palette (Ctrl+Shift+P):
- `Tasks: Run Task`
- Select a Lyra task

---

## Performance Tips

### Make Commands Faster
Commands can be slow the first time ROS starts. Speed them up:

```bash
# Option 1: Pre-start ROS daemon
ros2 daemon start

# Option 2: Add to ~/.bashrc (runs on every login)
ros2 daemon start 2>/dev/null || true
```

### Lazy Loading (Advanced)
Create a wrapper script for faster shell startup:
```bash
# ~/.bashrc
alias lyra='source ~/lyra_ws/lyra_commands.sh && lyra'
```

This delays loading the functions until you actually use a `lyra-*` command.

---

## Uninstall

To remove the command utility:

```bash
# Remove from ~/.bashrc
sed -i '/lyra_commands.sh/d' ~/.bashrc

# Optional: Delete script files
rm ~/lyra_ws/lyra_commands.sh
rm ~/lyra_ws/lyra_doctor.sh

# Reload shell
source ~/.bashrc
```

---

## Support & Debugging

### Get Help
```bash
lyra-help              # Full documentation
lyra-commands          # List all commands
lyra-help | grep arm   # Find commands about arming
```

### Run Diagnostics
```bash
./lyra_doctor.sh --verbose     # Full system check
./lyra_doctor.sh --fix         # Auto-fix issues
```

### Check Setup is Correct
```bash
# Verify script is sourced
declare -f lyra-help      # Should show function code

# List all lyra- commands
declare -F | grep lyra-   # Should show many functions

# Check workspace path
echo $LYRA_WS             # Should show workspace location
```

### Common Issues

**Commands not found after adding to ~/.bashrc:**
- Restart your terminal (not just reloading)
- Or run: `exec bash` to start a new shell

**ROS commands timeout:**
- Run: `ros2 daemon start`
- Then: `ros2 daemon stop && ros2 daemon start` to reset

**Workspace errors:**
- Verify workspace is built: `ls ~/lyra_ws/install`
- Rebuild if needed: `cd ~/lyra_ws && colcon build`

---

## Files Included

1. **lyra_commands.sh** - Main command utility
   - 40+ useful commands
   - Help system
   - Parameter management
   - Node control

2. **lyra_doctor.sh** - Diagnostic script
   - Hardware checks
   - ROS network checks
   - Auto-fix capabilities
   - System health monitoring

3. **LYRA_QUICK_REFERENCE.md** - Quick reference card
   - Common workflows
   - Troubleshooting guide
   - Useful aliases
   - Emergency procedures

4. **LYRA_COMMAND_UTILITY_SETUP.md** - This file
   - Installation instructions
   - Setup guide
   - Troubleshooting

---

## Version History

- **v1.0** (2026-01-18)
  - Initial release
  - 40+ commands
  - Full diagnostic script
  - Comprehensive documentation

---

## Feedback & Improvements

If you find issues or have improvement ideas:

1. Test with `./lyra_doctor.sh --verbose`
2. Check if command is documented: `lyra-help`
3. Report specific command issues with:
   ```bash
   lyra-node-info <node_name>
   ```

---

**Created:** 2026-01-18  
**Compatible with:** Lyra V4.4 Robot  
**Requires:** ROS 2 Humble (or newer)

