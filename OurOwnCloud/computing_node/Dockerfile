# 基底映像：Python + ffmpeg（音訊處理常用）
FROM python:3.10-slim

# 安裝 ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean

# 建立工作目錄
WORKDIR /app

# 複製程式與依賴
COPY audio_processing.py /app/
COPY computing.py /app/
COPY requirements.txt /app/

# 安裝 Python 套件
RUN pip install --upgrade pip && pip install -r requirements.txt

# 設定開機後執行的指令
#CMD ["python", "computing.py"]
