# LYRA ROBOT COMMANDS - WINDOWS/WSL SETUP GUIDE

If you're running on Windows with WSL (Windows Subsystem for Linux), this guide will help you set up the command utility.

---

## Option A: WSL 2 (Recommended)

### Prerequisites
- Windows 10/11 with WSL 2 installed
- Ubuntu 20.04 or 22.04 in WSL
- ROS 2 installed in WSL
- Your Lyra workspace in WSL

### Setup Steps

#### 1. Open WSL Terminal
```powershell
# In PowerShell or Command Prompt
wsl
```

#### 2. Copy Command Files
```bash
# From Windows path to WSL
cp /mnt/d/STM/STM32F405RGTx/ROS\ Code/lyra_v4.4_parameterized-claude/lyra_commands.sh ~/lyra_ws/
cp /mnt/d/STM/STM32F405RGTx/ROS\ Code/lyra_v4.4_parameterized-claude/lyra_doctor.sh ~/lyra_ws/
chmod +x ~/lyra_ws/lyra_*.sh
```

#### 3. Enable in WSL Shell
```bash
echo "source ~/lyra_ws/lyra_commands.sh" >> ~/.bashrc
source ~/.bashrc
```

#### 4. Test It
```bash
lyra-help
```

---

## Option B: Git Bash (Windows Native)

If you prefer to stay on Windows:

### Prerequisites
- Git Bash installed
- ROS 2 for Windows (if available, experimental)

### Setup Steps

#### 1. Copy Files
```bash
# In Git Bash
cp /d/STM/STM32F405RGTx/ROS\ Code/lyra_v4.4_parameterized-claude/lyra_commands.sh ~/lyra_ws/
```

#### 2. Modify Script for Git Bash
Edit `lyra_commands.sh` and change:

**Line 7:**
```bash
# FROM:
LYRA_WS="${HOME}/lyra_ws"

# TO:
LYRA_WS="$(cd ~/lyra_ws && pwd)"
```

**Add near top (after line 40):**
```bash
# Git Bash compatibility
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    # Git Bash doesn't have lsof
    lyra_check_serial_in_use() {
        echo "Serial port in use check not available on Windows"
    }
fi
```

#### 3. Source in Git Bash
```bash
# In ~/.bash_profile
echo "source ~/lyra_ws/lyra_commands.sh" >> ~/.bash_profile
source ~/.bash_profile
```

#### 4. Limitations on Windows
⚠️ Some commands won't work on Windows:
- `lyra-test-hardware` (device access)
- `lyra-serial` checks
- Some diagnostics
- Permission/group checks

✅ These will work:
- All launch commands
- All ARM/DISARM commands
- Monitoring commands
- Node management
- Parameter commands

---

## Option C: Docker Container (Best for Testing)

### Setup

#### 1. Create Dockerfile
```dockerfile
FROM osrf/ros:humble-desktop

RUN apt-get update && apt-get install -y \
    git \
    nano \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy your workspace
COPY . /root/lyra_ws

WORKDIR /root/lyra_ws

# Source ROS
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc && \
    echo "source ~/lyra_ws/lyra_commands.sh" >> ~/.bashrc

CMD ["/bin/bash"]
```

#### 2. Build & Run
```powershell
# From Windows PowerShell
docker build -t lyra-robot .
docker run -it lyra-robot

# Inside container:
lyra-help
```

---

## Recommended Setup: WSL 2 + VSCode

This is the best experience for Windows users developing on Lyra:

### Step 1: Install VSCode Extensions
In VSCode:
1. Install "Remote - WSL" extension (Microsoft)
2. Install "ROS" extension (Microsoft)
3. Install "Bash IDE" extension

### Step 2: Open WSL Folder
1. Ctrl+K Ctrl+O
2. Select `/home/<user>/lyra_ws` in WSL
3. VSCode opens in WSL context

### Step 3: Use Integrated Terminal
- Ctrl+` opens integrated terminal
- Automatically in WSL
- Commands work directly:
  ```bash
  lyra-launch-robot-teleop
  lyra-arm
  ```

### Step 4: Create VSCode Tasks
Create `.vscode/tasks.json`:
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Lyra: Launch Teleop",
            "type": "shell",
            "command": "source ~/.bashrc && lyra-launch-robot-teleop",
            "isBackground": true,
            "runOptions": {"instanceLimit": 1}
        },
        {
            "label": "Lyra: Doctor Check",
            "type": "shell",
            "command": "source ~/.bashrc && ./lyra_doctor.sh --verbose"
        }
    ]
}
```

Run with Ctrl+Shift+B

---

## WSL-Specific Tips

### Serial Port Access from WSL
To access your STM32 board from WSL:

```bash
# List available COM ports (in PowerShell, not WSL)
Get-PnPDevice -PresentOnly | Where-Object {$_.InstanceId -match "COM"}
# Example output: COM3

# In WSL, map it:
# /dev/ttyS3 corresponds to COM3 (S + port number)
```

Update `lyra_params.yaml`:
```yaml
serial:
  port: /dev/ttyS3    # Changed from /dev/ttyAMA0 (RPi serial)
  baudrate: 115200
```

### File Path Conversion
Windows path → WSL path:
```
Windows: D:\ROS Code\lyra_v4.4
WSL:     /mnt/d/ROS\ Code/lyra_v4.4
```

### Copy Files Between Windows and WSL
```bash
# Windows → WSL
cp /mnt/d/Windows/path/file.sh ~/lyra_ws/

# WSL → Windows
cp ~/lyra_ws/file.sh /mnt/d/Windows/path/
```

### Performance Note
⚠️ WSL 2 is slower with disk I/O. If commands are slow:

1. Put workspace in WSL filesystem (`/home/user/lyra_ws`), not `/mnt/d/...`
2. Use fast SSD (WSL 2 needs this)
3. Consider Docker for better isolation

---

## Remote Development Setup

If your robot is on a Raspberry Pi and you develop on Windows:

### Option 1: SSH + VSCode Remote
```bash
# In VSCode
# 1. Install "Remote - SSH" extension
# 2. Click "Open Remote Window" (bottom left)
# 3. "Connect to Host..."
# 4. Enter: user@robot.local (or robot's IP)
# 5. Browse /home/user/lyra_ws
# 6. Terminal automatically connects via SSH
```

Then commands work on the robot:
```bash
lyra-launch-robot-teleop
lyra-arm
# Controls the actual robot!
```

### Option 2: Manual SSH
```bash
ssh user@robot.local
source ~/lyra_ws/lyra_commands.sh
lyra-help
```

---

## Troubleshooting Windows Setup

### "Command not found: lyra-*"
```bash
# Verify script sourced
cat ~/.bashrc | grep lyra_commands

# Source manually
source ~/lyra_ws/lyra_commands.sh

# Test
lyra-help
```

### "Permission denied" on script
```bash
# Make executable in WSL
chmod +x ~/lyra_ws/lyra_commands.sh
```

### Serial port issues on WSL
```bash
# List available ports
ls /dev/ttyS*
ls /dev/ttyUSB*

# If using USB adapter (more common):
# /dev/ttyUSB0 usually works directly

# Check permissions
ls -la /dev/ttyUSB0
```

### Slow launches from Windows/WSL
- Put workspace in WSL filesystem: `/home/user/lyra_ws` (not `/mnt/d`)
- Don't use network drives
- Use local SSD, not USB drives

### Docker permissions
```powershell
# Ensure Docker Desktop is running
docker --version

# If error: start Docker Desktop from Start menu
```

---

## Comparison: Which Option?

| Option | Ease | Performance | Features | Hardware |
|--------|------|-------------|----------|----------|
| WSL 2 | ⭐⭐⭐ | ⭐⭐ | ✅ Full | Linux apps |
| Git Bash | ⭐⭐ | ⭐⭐⭐ | ❌ Limited | Native Windows |
| Docker | ⭐⭐⭐ | ⭐ | ✅ Full | Any |
| SSH to Pi | ⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Full | Robot |

**Recommended:** WSL 2 + VSCode for best experience

---

## Quick Start: WSL 2

```powershell
# PowerShell on Windows
# 1. Open WSL
wsl

# 2. Copy files (inside WSL)
cp /mnt/d/STM/STM32F405RGTx/ROS\ Code/lyra_v4.4_parameterized-claude/lyra_commands.sh ~/lyra_ws/
chmod +x ~/lyra_ws/lyra_commands.sh

# 3. Enable
echo "source ~/lyra_ws/lyra_commands.sh" >> ~/.bashrc
source ~/.bashrc

# 4. Test
lyra-help

# 5. Done! Use from any WSL terminal
lyra-launch-robot-teleop
```

---

## Environment Variables (WSL Only)

If ROS is not sourcing automatically:

```bash
# Add to ~/.bashrc
export ROS_DISTRO=humble
source /opt/ros/$ROS_DISTRO/setup.bash
export ROS_DOMAIN_ID=42

# For networked robots
export ROS_LOCALHOST_ONLY=0
export ROS_DISCOVERY_SERVER=192.168.1.100:11511
```

---

## Need Help?

### Test Your Setup
```bash
# In your terminal (Windows/WSL/Docker/SSH)
source ~/lyra_ws/lyra_commands.sh
lyra-test-connectivity
```

### Check Workspace
```bash
echo $LYRA_WS
ls $LYRA_WS
```

### Verify ROS
```bash
source /opt/ros/$ROS_DISTRO/setup.bash
ros2 --version
```

---

## Next Steps

1. **Choose your setup** (WSL 2 recommended)
2. **Follow setup steps** for your option
3. **Test with** `lyra-help`
4. **Start using** `lyra-launch-robot-teleop`

You're all set! 🚀

---

Created: January 18, 2026  
For: Windows developers working with Lyra V4.4 robot  
Tested on: Windows 11 + WSL 2 + Ubuntu 22.04

