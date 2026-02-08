#!/usr/bin/env node

// format-table.js - Utility for creating formatted tables in CLI applications

// For Node.js applications, using cli-table3
// Dynamically require cli-table3 to handle cases where it might not be available
let Table;
try {
  Table = require('cli-table3');
} catch (e) {
  // Fallback if cli-table3 is not available
  console.error('cli-table3 is not installed. Please run: npm install cli-table3');
  Table = null;
}

/**
 * Creates a formatted table with specified options
 * @param {Array<Array<string>>} rows - Table data as array of rows
 * @param {Object} options - Table formatting options
 * @returns {string} Formatted table as string
 */
function createTable(rows, options = {}) {
  const table = new Table({
    head: options.headers || [],
    colWidths: options.colWidths || undefined,
    style: {
      head: ['cyan', 'bold'],
      border: ['grey'],
    }
  });

  // Add rows to the table
  for (const row of rows) {
    table.push(row);
  }

  return table.toString();
}

/**
 * Creates a horizontal line separator
 * @param {number} length - Length of the separator
 * @returns {string} Separator line
 */
function createSeparator(length = 50) {
  return '='.repeat(length);
}

/**
 * Creates a box around content
 * @param {string} content - Content to put in a box
 * @param {Object} options - Box options
 * @returns {string} Content in a box
 */
function createBox(content, options = {}) {
  const width = options.width || Math.max(...content.split('\n').map(line => line.length)) + 4;
  const topLine = '┌' + '─'.repeat(width - 2) + '┐';
  const bottomLine = '└' + '─'.repeat(width - 2) + '┘';

  const paddedContent = content.split('\n')
    .map(line => '│ ' + line.padEnd(width - 4) + ' │')
    .join('\n');

  return `${topLine}\n${paddedContent}\n${bottomLine}`;
}

// Example usage
if (require.main === module) {
  // Example 1: Simple table
  console.log('Example Table:');
  const tableData = [
    ['Name', 'Age', 'City'],
    ['John', '30', 'New York'],
    ['Jane', '25', 'Los Angeles'],
    ['Bob', '35', 'Chicago']
  ];

  const table = createTable(tableData, {
    headers: ['Name', 'Age', 'City'],
    colWidths: [15, 10, 15]
  });

  console.log(table);
  console.log('\n' + createSeparator() + '\n');

  // Example 2: Content in a box
  console.log(createBox('This is content in a box!\nMultiple lines work too.'));
}

module.exports = {
  createTable,
  createSeparator,
  createBox
};