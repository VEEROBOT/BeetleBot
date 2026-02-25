# LYRA ROBOT - COMMAND UTILITY & DOCUMENTATION INDEX

**Created:** January 18, 2026  
**Status:** Ready to Use

---

## 📋 Quick Navigation

### Getting Started (Choose Your Path)

**I'm on Linux/RPi:**
→ Read [LYRA_COMMAND_UTILITY_SETUP.md](LYRA_COMMAND_UTILITY_SETUP.md) → [LYRA_QUICK_REFERENCE.md](LYRA_QUICK_REFERENCE.md)

**I'm on Windows with WSL:**
→ Read [WINDOWS_WSL_SETUP_GUIDE.md](WINDOWS_WSL_SETUP_GUIDE.md) → [LYRA_COMMAND_UTILITY_SETUP.md](LYRA_COMMAND_UTILITY_SETUP.md)

**I want to understand the codebase:**
→ Read [STATIC_ANALYSIS_FINDINGS.md](STATIC_ANALYSIS_FINDINGS.md)

**I just want to run the robot:**
→ Read [LYRA_QUICK_REFERENCE.md](LYRA_QUICK_REFERENCE.md) and jump to "Daily Operations"

---

## 📁 Files in This Package

### Command Scripts (Executable)
```
lyra_commands.sh          ← Main command utility (40+ commands)
lyra_doctor.sh           ← Automated diagnostics & self-heal
```

### Documentation (Read These)
```
COMMAND_UTILITY_README.md              ← Overview & features
LYRA_COMMAND_UTILITY_SETUP.md          ← Installation guide
LYRA_QUICK_REFERENCE.md               ← Daily operations cheat sheet
WINDOWS_WSL_SETUP_GUIDE.md            ← Setup for Windows users
STATIC_ANALYSIS_FINDINGS.md           ← Code review (30 issues found)
```

### Index & Navigation
```
INDEX.md                              ← This file
```

---

## 🚀 Quick Start (5 Minutes)

### For Linux/RPi Users:
```bash
# 1. Copy files
cp lyra_commands.sh ~/lyra_ws/
chmod +x ~/lyra_ws/lyra_commands.sh

# 2. Enable commands
echo "source ~/lyra_ws/lyra_commands.sh" >> ~/.bashrc
source ~/.bashrc

# 3. Verify setup
lyra-help

# 4. Use it!
lyra-launch-robot-teleop
lyra-arm
lyra-battery
```

### For Windows/WSL Users:
```powershell
# In PowerShell
wsl

# Inside WSL:
cp /mnt/d/STM/STM32F405RGTx/ROS\ Code/lyra_v4.4_parameterized-claude/lyra_commands.sh ~/lyra_ws/
echo "source ~/lyra_ws/lyra_commands.sh" >> ~/.bashrc
source ~/.bashrc
lyra-help
```

---

## 📚 Documentation Overview

### 1. **COMMAND_UTILITY_README.md** - Overview
What you get, quick start, features, customization.
- **Read this first** to understand what's included
- 5-minute overview

### 2. **LYRA_COMMAND_UTILITY_SETUP.md** - Installation
Detailed installation steps, troubleshooting, advanced setup.
- **Read this** to install properly
- IDE integration, custom aliases, performance tips
- Troubleshooting for common setup issues

### 3. **LYRA_QUICK_REFERENCE.md** - Daily Operations
Command cheat sheet, troubleshooting matrix, workflows.
- **Print this or bookmark it**
- Fast lookup for common tasks
- Troubleshooting guide
- Emergency procedures

### 4. **WINDOWS_WSL_SETUP_GUIDE.md** - Windows Users
Special setup instructions for Windows 10/11 with WSL.
- **Read this if on Windows**
- WSL 2 setup (recommended)
- Git Bash setup
- Docker setup
- Remote development via SSH

### 5. **STATIC_ANALYSIS_FINDINGS.md** - Code Review
Detailed static analysis of your codebase.
- **Read this** for development/debugging
- 6 critical issues found
- 8 high-priority issues
- 11 medium-priority issues
- Detailed explanations and fixes

---

## 🎯 Common Tasks

### I want to...

#### Launch and test the robot
```bash
lyra-launch-robot-teleop
lyra-arm
# Use joystick
lyra-disarm
```
📖 See: LYRA_QUICK_REFERENCE.md → "Session 1: Teleop Testing"

#### Map the environment (SLAM)
```bash
lyra-launch-robot-slam
lyra-arm
# Drive around
ros2 run nav2_map_server map_saver_cli -f ~/maps/mymap
```
📖 See: LYRA_QUICK_REFERENCE.md → "Session 2: SLAM Mapping"

#### Run autonomous navigation
```bash
lyra-launch-robot-nav ~/maps/mymap.yaml
lyra-arm
# Set initial pose in RViz, click navigation goals
```
📖 See: LYRA_QUICK_REFERENCE.md → "Session 3: Navigation Testing"

#### Debug an issue
```bash
lyra-status
lyra-test-hardware
./lyra_doctor.sh --verbose
```
📖 See: LYRA_QUICK_REFERENCE.md → "Troubleshooting Matrix"

#### Check robot health
```bash
./lyra_doctor.sh
```
📖 See: LYRA_COMMAND_UTILITY_SETUP.md → "Doctor Script Setup"

#### View all available commands
```bash
lyra-help
lyra-commands
```
📖 In-script help with `lyra-help`

---

## 🔧 What's Included

### 40+ Pre-built Commands

**Launch (8):** base, SLAM, nav, teleop, bridge, RViz, variants
**Control (6):** arm, disarm, stop, ROS mode controls
**Monitor (8):** battery, RPM, IMU, LiDAR, odom, diagnostics
**Manage (4):** nodes, topics, services, details
**Params (3):** list, get, set
**Cleanup (5):** kill, reset, cleanup, helpers
**Test (2):** hardware, connectivity
**Help (2):** help, commands list

### Diagnostic System
- Hardware connectivity checks
- ROS network verification
- Robot health monitoring
- Auto-fix capabilities
- Verbose logging

### Documentation
- This index
- Installation guide
- Quick reference card
- Windows/WSL guide
- Code review report

---

## ✅ Features

✅ **Fast** - Single commands for complex operations  
✅ **Safe** - Confirmations for dangerous operations  
✅ **Clear** - Color-coded output, helpful messages  
✅ **Complete** - 40+ useful commands  
✅ **Smart** - Auto-detection and recovery  
✅ **Documented** - Comprehensive guides and help  

---

## 🏥 Troubleshooting

### Common Issues

**"Command not found: lyra-*"**
→ See: LYRA_COMMAND_UTILITY_SETUP.md → "Troubleshooting Setup"

**"Serial port error"**
→ See: LYRA_QUICK_REFERENCE.md → "Robot won't arm?" or run `./lyra_doctor.sh`

**"Motor won't move"**
→ See: LYRA_QUICK_REFERENCE.md → "Troubleshooting Matrix"

**"I'm on Windows"**
→ See: WINDOWS_WSL_SETUP_GUIDE.md

**"Complete system diagnostics"**
→ Run: `./lyra_doctor.sh --verbose`

---

## 📖 Reading Order (By Use Case)

### I'm a First-Time User
1. [COMMAND_UTILITY_README.md](COMMAND_UTILITY_README.md) - 5 min overview
2. [LYRA_COMMAND_UTILITY_SETUP.md](LYRA_COMMAND_UTILITY_SETUP.md) - Install
3. [LYRA_QUICK_REFERENCE.md](LYRA_QUICK_REFERENCE.md) - Daily operations

### I'm Debugging an Issue
1. Run: `./lyra_doctor.sh --verbose`
2. [LYRA_QUICK_REFERENCE.md](LYRA_QUICK_REFERENCE.md) → "Troubleshooting Matrix"
3. [STATIC_ANALYSIS_FINDINGS.md](STATIC_ANALYSIS_FINDINGS.md) → if code-level

### I'm a Developer
1. [STATIC_ANALYSIS_FINDINGS.md](STATIC_ANALYSIS_FINDINGS.md) - Code review
2. Look at specific issues mentioned
3. [LYRA_QUICK_REFERENCE.md](LYRA_QUICK_REFERENCE.md) → Testing section

### I'm on Windows
1. [WINDOWS_WSL_SETUP_GUIDE.md](WINDOWS_WSL_SETUP_GUIDE.md) - Setup guide
2. [LYRA_COMMAND_UTILITY_SETUP.md](LYRA_COMMAND_UTILITY_SETUP.md) - General setup
3. [LYRA_QUICK_REFERENCE.md](LYRA_QUICK_REFERENCE.md) - Use commands

---

## 💡 Tips & Tricks

### Print the Quick Reference Card
```bash
# Print to PDF or paper
cat LYRA_QUICK_REFERENCE.md | lp
# or
wc2pdf LYRA_QUICK_REFERENCE.md
```

### Create Custom Aliases
Add to ~/.bashrc:
```bash
alias ll='lyra-launch-robot-teleop'
alias la='lyra-arm'
alias ld='lyra-disarm'
alias lx='lyra-stop'
```

### Monitor Multiple Things
```bash
# Terminal 1: Launch
lyra-launch-robot-teleop

# Terminal 2: Battery
lyra-battery

# Terminal 3: Diagnostics
watch ./lyra_doctor.sh
```

### Auto-Fix Common Issues
```bash
./lyra_doctor.sh --fix
```

---

## 📊 Code Quality Report

A comprehensive static analysis was performed. See [STATIC_ANALYSIS_FINDINGS.md](STATIC_ANALYSIS_FINDINGS.md) for:

- **6 Critical Issues** (must fix before production)
- **8 High Priority Issues** (fix before release)
- **11 Medium Priority Issues** (next sprint)
- **5 Low Priority Issues** (documentation)

**Total Issues Found:** 30  
**Estimated Fix Time:** 52 hours

---

## 🔗 Quick Links

| Need | File | Section |
|------|------|---------|
| Overview | COMMAND_UTILITY_README.md | Quick Start |
| Installation | LYRA_COMMAND_UTILITY_SETUP.md | Step 1-5 |
| Daily Use | LYRA_QUICK_REFERENCE.md | Daily Operations |
| Troubleshooting | LYRA_QUICK_REFERENCE.md | Troubleshooting Matrix |
| Windows Setup | WINDOWS_WSL_SETUP_GUIDE.md | Option A (WSL 2) |
| Code Issues | STATIC_ANALYSIS_FINDINGS.md | Critical Issues |

---

## 🚨 Emergency Procedures

### Robot won't stop
```bash
lyra-stop                # Emergency service call
lyra-kill                # Kill all nodes
```

### Serial connection lost
```bash
./lyra_doctor.sh --fix   # Auto-fix attempt
lyra-cleanup             # Full cleanup
```

### Need complete restart
```bash
lyra-reset               # Nuclear reset
lyra-launch-robot-teleop # Start fresh
```

See LYRA_QUICK_REFERENCE.md → "Emergency Procedures" for more.

---

## 📝 File Locations

When you copy the scripts to your workspace, they should be at:

```
~/lyra_ws/
├── lyra_commands.sh              ← Copy here
├── lyra_doctor.sh                ← Copy here
├── install/
├── build/
├── src/
└── ...
```

All documentation files are in your workspace root:
```
lyra_v4.4_parameterized-claude/
├── lyra_commands.sh
├── lyra_doctor.sh
├── COMMAND_UTILITY_README.md
├── LYRA_COMMAND_UTILITY_SETUP.md
├── LYRA_QUICK_REFERENCE.md
├── WINDOWS_WSL_SETUP_GUIDE.md
├── STATIC_ANALYSIS_FINDINGS.md
├── INDEX.md
└── ... (other files)
```

---

## 🎓 Learning Resources

These commands also teach ROS 2:
- Each command is a wrapper around ROS 2 CLI tools
- See what ROS 2 command is being called in the script
- Modify commands to learn

Example learning path:
1. Use: `lyra-status`
2. See in script: `ros2 node list`
3. Learn: `ros2 node list --help`
4. Explore: Create your own commands

---

## ⭐ Key Features Summary

| Feature | Benefit |
|---------|---------|
| 40+ Commands | No need to remember ROS 2 syntax |
| Auto-Discovery | Finds nodes, topics, services automatically |
| Color Output | Easy to spot errors and status |
| Diagnostics | Find and fix issues automatically |
| Confirmations | Prevents accidental data loss |
| Documentation | Comprehensive guides included |
| Extensible | Easy to add custom commands |

---

## 🔄 Getting Help

### In the Terminal
```bash
lyra-help              # Full documentation
lyra-commands          # List all commands
lyra-node-info <name>  # Details on a node
```

### In This Package
- Overview: COMMAND_UTILITY_README.md
- Installation: LYRA_COMMAND_UTILITY_SETUP.md  
- Quick Ref: LYRA_QUICK_REFERENCE.md
- Troubleshooting: LYRA_QUICK_REFERENCE.md
- Windows: WINDOWS_WSL_SETUP_GUIDE.md

### Diagnostic
```bash
./lyra_doctor.sh --verbose
```

---

## 📞 Support Workflow

**Step 1:** Run diagnostics
```bash
./lyra_doctor.sh --verbose
```

**Step 2:** Check Quick Reference
Open LYRA_QUICK_REFERENCE.md and find your issue in "Troubleshooting Matrix"

**Step 3:** Try recommended fix
Follow the suggested steps

**Step 4:** If still stuck
Check STATIC_ANALYSIS_FINDINGS.md for code-level issues

---

## 🎯 Next Steps

1. **Choose your setup** (Linux/Windows/WSL)
2. **Read the appropriate guide** (see Quick Navigation above)
3. **Install the scripts** (usually 5 minutes)
4. **Test with** `lyra-help`
5. **Start using** commands daily

---

## 📅 Version Info

- **Created:** January 18, 2026
- **For:** Lyra V4.4 Robot
- **Compatible with:** ROS 2 Humble (other versions likely work)
- **Tested on:** Linux, WSL 2, macOS
- **Total Commands:** 40+
- **Total Documentation:** 5 guides + this index

---

## 🙏 Summary

You now have a complete command utility system with:

✅ Ready-to-use launch, arm, monitor, and debug commands  
✅ Automated diagnostics system  
✅ Comprehensive troubleshooting guide  
✅ Setup instructions for your platform  
✅ Code quality report with 30 issues analyzed  

**Everything you need for daily operations and debugging!**

---

## 🚀 Ready to Start?

```bash
# Copy the files to your workspace
cp lyra_commands.sh ~/lyra_ws/
cp lyra_doctor.sh ~/lyra_ws/

# Enable them
echo "source ~/lyra_ws/lyra_commands.sh" >> ~/.bashrc
source ~/.bashrc

# Use them!
lyra-help
```

**You're all set! Happy roboting! 🤖**

---

**For questions or issues:** Check the relevant documentation file above.  
**For code issues:** See STATIC_ANALYSIS_FINDINGS.md  
**For setup issues:** See your platform's setup guide (Linux/Windows)  

