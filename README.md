LLM Quiz Solver - Complete Project
Generated: November 19, 2025
Purpose: LLM Analysis Quiz Project for IIT Madras
Evaluation Date: November 29, 2025, 3:00-4:00 PM IST

Table of Contents
Project Overview

Quick Start

Project Structure

File Contents

Installation Instructions

Testing Guide

Deployment Checklist

Project Overview
This is a complete, production-ready implementation of an LLM-powered quiz solver that:

✅ Accepts POST requests with quiz URLs

✅ Uses Playwright for JavaScript rendering

✅ Leverages OpenAI GPT-5-nano for task interpretation

✅ Processes PDFs, data analysis, and visualization tasks

✅ Handles sequential quiz chains

✅ Completes within 3-minute time constraint

✅ Includes comprehensive error handling

✅ Fully documented with MIT License

Total Files: 33 files across 7 directories

Quick Start
bash
# 1. Create project directory
mkdir llm-quiz-solver && cd llm-quiz-solver

# 2. Create directory structure
mkdir -p api browser llm processors utils tests

# 3. Copy all files (provided below)

# 4. Run setup
chmod +x setup.sh && ./setup.sh

# 5. Configure .env
cp .env.example .env
# Edit .env and add:
# - OPENAI_API_KEY
# - SECRET_KEY  
# - EMAIL

# 6. Test
python tests/test_basic.py

# 7. Start server
python main.py
Project Structure
text
llm-quiz-solver/
├── main.py                    # FastAPI entry point
├── config.py                  # Settings management
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── .gitignore                # Git ignore patterns
├── LICENSE                   # MIT License
├── README.md                 # Main documentation
├── QUICKSTART.md            # Quick start guide
├── ARCHITECTURE.md          # Architecture docs
├── D