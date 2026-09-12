# Flappy Bird

A small Flappy Bird-style game written in Python with Pygame.

## Features

* Gravity and jumping
* Animated bird
* Moving pipe obstacles
* Collision detection
* Score counter
* Persistent high score
* Game over and restart
* Simple generated sound effects
* Omarchy launcher support

## Controls

* `Space` — flap / jump
* `Esc` — quit

## Requirements

* Python 3
* Pygame

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install Pygame:

```bash
python -m pip install pygame
```

## Run

Start the game with:

```bash
python flappy.py
```

## Sound

The game uses three sound files:

```text
sounds/jump.wav
sounds/score.wav
sounds/hit.wav
```

They can be generated with:

```bash
python make_sounds.py
```

## High Score

The high score is saved automatically in:

```text
highscore.txt
```

This file is created by the game when needed.

## Project Structure

```text
FlappyBird/
├── flappy.py
├── make_sounds.py
├── highscore.txt
├── sounds/
│   ├── jump.wav
│   ├── score.wav
│   └── hit.wav
├── .gitignore
└── README.md
```

## About

This project was built as a small Python/Pygame learning project on Omarchy.

The goal was to create a complete playable game with simple physics, collision detection, scoring, persistent data, sound, and a desktop launcher.

## Screenshots

![Flappy Bird gameplay](screenshot-2026-09-12_20-54-40.png)
