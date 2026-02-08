#!/usr/bin/env node

// colorize-output.js - Functions for applying consistent color schemes to CLI output

// Dynamically require chalk to handle cases where it might not be available
let chalk;
try {
  chalk = require('chalk');
} catch (e) {
  // Fallback if chalk is not available
  chalk = {
    green: (str) => str,
    red: (str) => str,
    yellow: (str) => str,
    blue: (str) => str,
    gray: (str) => str,
    cyan: (str) => str,
    magenta: (str) => str,
    white: (str) => str,
    bold: (str) => str
  };
  // Create compound functions for the expected combinations
  chalk.green.bold = (str) => str;
  chalk.red.bold = (str) => str;
  chalk.yellow.bold = (str) => str;
  chalk.blue.bold = (str) => str;
  chalk.cyan.bold = (str) => str;
  chalk.magenta.bold = (str) => str;
  chalk.magenta.bold.underline = (str) => str;
}

/**
 * Color schemes for different types of messages
 */
const colorSchemes = {
  success: chalk.green.bold,
  error: chalk.red.bold,
  warning: chalk.yellow.bold,
  info: chalk.blue.bold,
  debug: chalk.gray,
  highlight: chalk.cyan.bold,
  title: chalk.magenta.bold.underline,
  subtle: chalk.gray
};

/**
 * Applies consistent color formatting to messages
 * @param {string} type - Type of message (success, error, warning, info, etc.)
 * @param {string} message - The message to colorize
 * @returns {string} Colorized message
 */
function colorize(type, message) {
  const colorFn = colorSchemes[type] || chalk.white;
  return colorFn(message);
}

/**
 * Creates a formatted message with an icon
 * @param {string} type - Type of message
 * @param {string} message - The message content
 * @returns {string} Formatted message with icon
 */
function formatMessage(type, message) {
  const icons = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️',
    debug: '🐛',
    highlight: '✨',
    title: '🎯',
    subtle: '🔸'
  };

  const icon = icons[type] || '🔹';
  const colorFn = colorSchemes[type] || chalk.white;

  return `${icon} ${colorFn(message)}`;
}

/**
 * Creates a status banner with consistent styling
 * @param {string} title - Banner title
 * @param {string} status - Status message
 * @param {string} color - Color for the status
 * @returns {string} Formatted banner
 */
function createStatusBanner(title, status, color = 'info') {
  const colorFn = colorSchemes[color];
  const statusText = colorFn ? colorFn(status) : status;

  const banner = `
┌─────────────────────────────────────────────────────────┐
│  ${chalk.bold(title)}${' '.repeat(48 - title.length)} │
│  Status: ${statusText}${' '.repeat(39 - status.length)} │
└─────────────────────────────────────────────────────────┘
`;

  return banner;
}

/**
 * Formats a list of items with consistent styling
 * @param {Array<string>} items - List of items to format
 * @param {string} title - Optional title for the list
 * @returns {string} Formatted list
 */
function formatList(items, title = '') {
  if (title) {
    console.log(chalk.bold.blue(`\n${title}\n`));
  }

  items.forEach((item, index) => {
    console.log(`${chalk.cyan(`  ${index + 1}.`)} ${item}`);
  });
}

// Example usage
if (require.main === module) {
  console.log(formatMessage('title', 'CLI Beautification Examples'));
  console.log('');
  console.log(formatMessage('success', 'Operation completed successfully'));
  console.log(formatMessage('error', 'An error occurred'));
  console.log(formatMessage('warning', 'This is a warning message'));
  console.log(formatMessage('info', 'Here is some information'));
  console.log(formatMessage('debug', 'Debug information'));

  console.log(createStatusBanner('My CLI Application', 'Running', 'success'));

  formatList([
    'Task 1: Initialize project',
    'Task 2: Install dependencies',
    'Task 3: Build application',
    'Task 4: Run tests'
  ], 'Build Process');
}

module.exports = {
  colorize,
  formatMessage,
  createStatusBanner,
  formatList,
  colorSchemes
};