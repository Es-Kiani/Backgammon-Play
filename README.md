# Backgammon

A classic Backgammon game implemented in Python using Pygame. This repository features both **offline** play and **LAN multiplayer**, with robust game management utilities like save/load, move history (undo/redo), per-player timers, and clear separation of concerns (game logic, UI, networking).

---

## 🚀 Key Features

- **Standard Backgammon Rules**: Full support for dice rolling, checker movements, hitting/blots, bar entry, and bearing off.
- **Graphical User Interface**: 
  - Animated dice rolling
  - Highlighting valid moves
  - Real-time sidebar with player turn, phase, clocks, blocked points, and borne-off counts
- **Game Persistence**:
  - **Save Game**: Export current state to a YAML file
  - **Load Game**: Resume from previously saved files
- **Move History & Navigation**:
  - Full undo/redo stack
  - Step backward or forward through each move in the game
- **Per-Player Timers**:
  - Individual clocks track cumulative thinking time
  - Pause/resume automatically on turn changes
- **Offline & LAN Play**:
  - **Offline Mode**: Local two-player game (control both sides)
  - **Host (LAN)**: Start a server, share IP/port, host plays White
  - **Join (LAN)**: Connect to host IP, join as Black
- **Clean Architecture**:
  - `game.py`: Core rules and state management
  - `ui.py`: Pygame-based rendering and input
  - `network.py`: Client/server communication
  - `app.py`: High-level coordination and state transitions

---

## 📋 Table of Contents

- [Backgammon](#backgammon)
  - [🚀 Key Features](#-key-features)
  - [📋 Table of Contents](#-table-of-contents)
  - [🛠️ Installation](#️-installation)
  - [⚙️ Configuration](#️-configuration)
  - [▶️ Usage](#️-usage)
    - [Main Menu Options](#main-menu-options)
  - [💾 Game Persistence](#-game-persistence)
    - [Saving a Game](#saving-a-game)
    - [Loading a Game](#loading-a-game)
  - [🔄 Move History \& Undo/Redo](#-move-history--undoredo)
  - [⏱️ Timers](#️-timers)
  - [🗂️ Project Structure](#️-project-structure)
  - [🤝 Contributing](#-contributing)
  - [🐞 Troubleshooting](#-troubleshooting)
  - [📄 License](#-license)

---

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/Backgammon.git
   cd Backgammon
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # macOS/Linux
   .\venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

> **Tip:** If you don’t have `requirements.txt`, install directly:
> ```bash
> pip install pygame pyyaml
> ```

---

## ⚙️ Configuration

The project uses a `config.yaml` for default network settings. Example:

```yaml
network:
  default_host_ip: "192.168.3.96"  # Your machine's IP
  default_port: 5555               # Default listening port
```

Place your own values in `config.yaml` or rely on the defaults.

---

## ▶️ Usage

Launch the game from the project root:

```bash
python main.py
```

### Main Menu Options

- **Play Offline**: Control both White and Black locally.
- **Host Game (LAN)**:
  1. Enter or confirm IP and port.
  2. Click **Start Hosting**.
  3. Wait for a client to connect.
- **Join Game (LAN)**:
  1. Enter the host’s IP address.
  2. Click **Join**.

Use mouse clicks on the board and sidebar buttons for all interactions.

---

## 💾 Game Persistence

### Saving a Game

1. From the in-game sidebar, click **Save Game**.
2. Choose a filename (e.g., `game1.yaml`).
3. The current position, move history, and timers are stored.

### Loading a Game

1. From the main menu, click **Load Game**.
2. Select a previously saved YAML file.
3. The game resumes from that exact state.

---

## 🔄 Move History & Undo/Redo

- **Undo**: Step back one move. Available until the start of the game.
- **Redo**: Step forward through undone moves.
- **History Panel**: Shows a chronological list of moves.

Controls are via sidebar buttons or **Ctrl+Z** (undo), **Ctrl+Y** (redo).

---

## ⏱️ Timers

Each player has an independent clock:
- **Start**: Timer begins when the opponent completes their turn.
- **Pause/Resume**: Automatically toggles on turn change.
- **Display**: Visible in sidebar as `White Time: mm:ss`, `Black Time: mm:ss`.

Timers are saved/loaded along with game state.

---

## 🗂️ Project Structure

```
Backgammon/
├── main.py             # Launches App
├── app.py              # Orchestrates UI, logic, and network
├── game.py             # Core Backgammon rules & state
├── network.py          # Networking via TCP sockets
├── ui.py               # Rendering and event helpers
├── config.yaml         # Default network settings
├── README.md           # (This file)
├── requirements.txt    # pygame, pyyaml
└── images/             # Static assets (background, icons)
```

---

## 🤝 Contributing

Contributions are welcome! To contribute:
1. Fork the repository
2. Create a branch: `git checkout -b feature/YourFeature`
3. Commit your changes
4. Push to your fork
5. Open a Pull Request

Please follow the existing code style and add tests for new functionality.

---

## 🐞 Troubleshooting

- **Cannot bind port**: Ensure no other service is using the configured port.
- **Firewall issues**: Allow Python or the chosen port through your firewall.
- **Missing dependencies**: Run `pip install pygame pyyaml`.
- **Corrupted save file**: Check YAML syntax and retry.

For other issues, please open an issue on GitHub.

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

*Enjoy your game!*

