import 'dotenv/config';
import { InstallGlobalCommands } from './utils.js';

// Simple test command
const TEST_COMMAND = {
  name: 'test',
  description: 'Basic command',
  type: 1,
  integration_types: [0, 1],
  contexts: [0, 1, 2],
};

const SEND_IMAGE_COMMAND = {
  name: 'send_image',
  description: 'You better wake up soon',
  type: 1,
  integration_types: [0, 1],
  contexts: [0, 2],
};

const ALL_COMMANDS = [TEST_COMMAND, SEND_IMAGE_COMMAND];

InstallGlobalCommands(process.env.APP_ID, ALL_COMMANDS);
