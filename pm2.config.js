module.exports = {
  apps: [
    {
      name: 'llm-chat-api',
      interpreter: 'bash',
      script: './run.sh',
      cwd: '/opt/llm-chat',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '3G',
      env: {
        API_HOST: '0.0.0.0',
        API_PORT: '8000',
        LOG_LEVEL: 'INFO',
        PYTHONUNBUFFERED: '1',
      },
      error_file: '/opt/llm-chat/logs/error.log',
      out_file: '/opt/llm-chat/logs/out.log',
      log_file: '/opt/llm-chat/logs/combined.log',
      time: true,
      merge_logs: true,
      kill_timeout: 5000,
      wait_ready: true,
      listen_timeout: 10000,
    },
  ],
}
