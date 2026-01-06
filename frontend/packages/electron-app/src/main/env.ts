import path from 'node:path'

const REQUEST_WHITE_URL = [
  'http://127.0.0.1:1420/*',
  'http://127.0.0.1:8003/*',
  'http://127.0.0.1:8006/*',
  'http://dev.iflyrpa.private:31680/*',
  'http://test.iflyrpa.private:32680/*',
  'https://newapi.iflyrpa.com/*',
]

export const envJson = {
  DEV_URL: "http://localhost:1420/boot.html",
  APP_URL: path.join(__dirname, '../renderer/boot.html'),
  REQUEST_WHITE_URL,
  SCHEDULER_NAME: 'astronverse.scheduler',
}
