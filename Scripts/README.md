# Alarm of DEATH

This project consists of two main parts: a **History Logger** that saves your browser search history and an **Alarm System** that captures a photo from your webcam and sends it to Discord when triggered.

## Prerequisites

1.  **Environment Variables**: Ensure you have a `.env` file in the `Scripts/` directory with:
    ```env
    DISCORD_TOKEN=your_discord_bot_token
    CHANNEL_ID=your_discord_channel_id
    PUBLIC_KEY=your_discord_app_public_key
    APP_ID=your_discord_app_id
    ```
2.  **Dependencies**: Install the required Python packages:
    ```bash
    pip install flask requests python-dotenv opencv-python pynacl
    ```

3. Load the chrome extension in chrome://extensions

## How to Run

Run server.py and send_image_helper.py

To start search history logging, run history_logger.py

To run the image trigger, run send_image.py