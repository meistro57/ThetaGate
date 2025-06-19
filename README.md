# ThetaGate
EEG-powered hypnosis assistant for self-exploration and QHHT. Tracks trance depth and guides you deeper.
# ThetaGate 🧠🔮

**ThetaGate** is a real-time hypnosis + EEG feedback system for exploring deep trance states, analyzing QHHT sessions, and guiding consciousness with precision.

## Features
- Live brainwave visualization (Delta, Theta, Alpha, Beta)
- Custom hypnosis script playback with binaural support
- Real-time trance depth detection with scoring system
- EEG data logging + session replay
- QHHT practitioner dashboard (in development)

## Goals
- Help users self-hypnotize with real-time feedback
- Provide tools for QHHT practitioners to gauge trance depth
- Build an evolving subconscious interface

## Hardware Compatibility (planned)
- Muse 2 / Muse S
- OpenBCI (Cyton / Ganglion)
- Emotiv Insight / EPOC

## Roadmap
- [ ] MVP with live EEG and basic trance scoring
- [ ] Self-hypnosis script runner
- [ ] Session recording and tagging
- [ ] QHHT mode for guided sessions


## Getting Started

A simple CLI is included to demonstrate the basic functionality. No external
packages are required beyond Python 3.8+.

```bash
# Stream simulated EEG data
python -m thetagate monitor --interval 1

# Run a sample hypnosis script
python -m thetagate run-script scripts/sample.txt --delay 3
```

