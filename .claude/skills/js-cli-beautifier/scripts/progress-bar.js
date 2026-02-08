#!/usr/bin/env node

// progress-bar.js - Implementation of progress bars for CLI applications

// Dynamically require cli-progress to handle cases where it might not be available
let ProgressBar;
try {
  ProgressBar = require('cli-progress');
} catch (e) {
  // Fallback if cli-progress is not available
  console.error('cli-progress is not installed. Please run: npm install cli-progress');
  ProgressBar = null;
}

/**
 * Creates and manages a progress bar
 * @param {Object} options - Progress bar options
 * @returns {Object} Progress bar instance
 */
function createProgressBar(options = {}) {
  const barOptions = {
    format: options.format || 'Progress [{bar}] {percentage}% | {value}/{total}',
    barCompleteChar: '\u25A0',
    barIncompleteChar: '\u25A1',
    hideCursor: true,
    ...options
  };

  return new ProgressBar.SingleBar(barOptions);
}

/**
 * Creates a multi-bar progress display
 * @returns {Object} Multi-bar instance
 */
function createMultiBar() {
  return new ProgressBar.MultiBar({
    format: '{bar} {percentage}% | {jobID} | {value}/{total}',
    barCompleteChar: '\u25A0',
    barIncompleteChar: '\u25A1',
    hideCursor: true
  });
}

/**
 * Simulates a progress bar for demonstration
 * @param {number} total - Total number of steps
 * @param {number} delay - Delay between steps in ms
 */
function simulateProgressBar(total = 100, delay = 100) {
  const bar = createProgressBar();

  // Initialize the bar
  bar.start(total, 0);

  // Update the bar
  const timer = setInterval(() => {
    bar.increment();

    if (bar.getValue() >= total) {
      clearInterval(timer);
      bar.stop();
      console.log('\nProcess completed!');
    }
  }, delay);
}

// Example usage
if (require.main === module) {
  console.log('Starting progress bar simulation...\n');

  // Example 1: Simple progress bar
  simulateProgressBar(50, 200);
}

module.exports = {
  createProgressBar,
  createMultiBar,
  simulateProgressBar
};