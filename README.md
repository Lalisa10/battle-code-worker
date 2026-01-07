# battle-code-worker

Đây là thành phần worker cho hệ thống Battle Code, dùng để chạy code submission. Hiện tại hệ thống vẫn đang chỉ phục vụ cho game tic-tac-toe kích thước bảng 30, điều kiện thắng là 5.
## NSJail — cài đặt & cấu hình (ngắn gọn) 🔧

### 1) Cài đặt / build NSJail (Linux)
- Cài đặt trực tiếp trên máy:

```bash
# Install dependencies (Debian/Ubuntu)
sudo apt-get install autoconf bison flex gcc g++ git libprotobuf-dev libnl-route-3-dev libtool make pkg-config protobuf-compilerbash

git clone https://github.com/google/nsjail.git
cd nsjail
make
```

- Hoặc build Docker image từ `nsjail/Dockerfile` nếu bạn muốn chạy trong container, tuy nhiên cần cấu hình phức tạp hơn khi chạy:

    ```bash
    docker build -t nsjail nsjail/
    ```

### 2) Tạo file `.env`

Tạo file `.env` tại gốc repository với nội dung ví dụ sau:

```dotenv
# Board size (30 for tic-tac-toe)
BOARD_SIZE=30

# Number of consecutive pieces to win
WIN_CONDITION=5

# Time limit per move (milliseconds)
TIME_LIMIT_MS=1000


# =====================================================
# Replay output
# =====================================================

# Directory to store replay JSON files
REPLAY_DIR='/home/trucdnd/Documents/Projects/battle-code/replay'
BASE_SUBMISSION_DIR='/home/trucdnd/Documents/Projects/battle-code/uploads/submissions'

# =====================================================
# Worker / controller settings
# =====================================================

# Redis config
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_QUEUE=match_queue

# Python + game controller path
PYTHON_BIN=python3
GAME_CONTROLLER_PATH=tic-tac-toe/game_controller.py

# Backend API for match updates
BACKEND_BASE_URL=http://localhost:8080
# BACKEND_TOKEN=
BACKEND_TIMEOUT=10

# NSJAIL paths
NSJAIL_BIN=nsjail/nsjail
NSJAIL_CONFIG=tic-tac-toe/game_config.cfg
NSJAIL_PYTHON=/usr/bin/python3
```

Trong đó các biến quan trọng như:
- `BASE_SUBMISSION_DIR`: thư mục chứa source submissions; sẽ được thay vào template `{{SUBMISSIONS_DIR}}`.
- `NSJAIL_CONFIG_TEMPLATE`: đường dẫn tới template (mặc định đã có `tic-tac-toe/game_config.cfg.tmpl`).
- `NSJAIL_BIN`: đường dẫn tới binary nsjail (mặc định `nsjail/nsjail` khi build nội bộ).
- `NSJAIL_PYTHON`: interpreter được gọi *inside* nsjail (ví dụ `/usr/bin/python3`).
- `TIME_LIMIT_MS`, `BOARD_SIZE`, `WIN_CONDITION`: thiết lập trò chơi.
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_QUEUE`: lấy trận đấu từ hàng đợi Redis

### 3) Chạy thử

- Chạy trực tiếp controller (ví dụ):

```bash
python3 tic-tac-toe/game_controller.py <match_id> <bot1_path> <bot2_path> <sub_id1> <sub_id2>
```
- Chạy chương trình chính:
```bash
python3 main.py
```

