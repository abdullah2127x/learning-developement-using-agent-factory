#!/usr/bin/env node

/**
 * Complete CLI Beautification Example
 *
 * This script demonstrates proper implementation of all CLI beautification features
 * with correct imports and error handling to avoid common issues.
 */

// Proper imports to avoid the issues encountered
const chalk = require('chalk');
const Table = require('cli-table3');
const cliProgress = require('cli-progress');
const boxen = require('boxen');  // Note: not destructured as {boxen}
const ora = require('ora');

// Enhanced header with styling
console.log(chalk.bold.blue('╔' + '═'.repeat(60) + '╗'));
console.log(chalk.bold.blue('║') + chalk.bold.bgBlue.white(' CLI BEAUTIFIER COMPLETE EXAMPLE ') + chalk.bold.blue('║'));
console.log(chalk.bold.blue('╚' + '═'.repeat(60) + '╝'));

// Enhanced message types with color coding
console.log('');
console.log(chalk.bold('ENHANCED MESSAGE TYPES:'));
console.log(chalk.green('✓ Success: Operation completed successfully'));
console.log(chalk.red('✗ Error: An error occurred during processing'));
console.log(chalk.yellow('⚠ Warning: This is a warning message'));
console.log(chalk.blue('ℹ Info: Here is some important information'));
console.log(chalk.gray('⚙ Debug: Debug information for troubleshooting'));

// Enhanced table using cli-table3
console.log('');
console.log(chalk.bold('ENHANCED TABLE:'));

const table = new Table({
    head: [chalk.bold.blue('Name'), chalk.bold.blue('Status'), chalk.bold.blue('Last Updated')],
    colWidths: [15, 15, 15],
    style: {
        head: ['blue', 'bold'],
        border: ['grey']
    }
});

table.push(
    [chalk.green('Project A'), chalk.green.bold('Active'), '2026-01-06'],
    [chalk.yellow('Project B'), chalk.yellow.bold('Warn'), '2026-01-05'],
    [chalk.red('Project C'), chalk.red.bold('Error'), '2026-01-04']
);

console.log(table.toString());

// Enhanced progress indicator using cli-progress
console.log('');
console.log(chalk.bold('ENHANCED PROGRESS INDICATION:'));

// Create a new progress bar
const progressBar = new cliProgress.SingleBar({
    format: 'Processing items |' + chalk.cyan('{bar}') + '| {percentage}% | {value}/{total} | {msg}',
    barCompleteChar: '\u25A0',
    barIncompleteChar: '\u25A1',
    hideCursor: true
});

// Initialize the bar - (total, starting value)
progressBar.start(5, 0);

// Simulate processing items with the progress bar
for (let i = 1; i <= 5; i++) {
    // Update the bar value
    progressBar.update(i, {
        msg: `Processing item ${i}/5`
    });

    // Simulate processing time
    const startTime = Date.now();
    while (Date.now() - startTime < 300); // 300ms delay
}

// Stop the bar
progressBar.stop();
console.log(chalk.green('\n✓ All items processed successfully!'));

// Example of using spinner for async operations
console.log('');
console.log(chalk.bold('SPINNER EXAMPLE:'));

// In a real async context, you would use:
// const spinner = ora('Loading...').start();
// try {
//   await asyncOperation();
//   spinner.succeed('Operation completed!');
// } catch (error) {
//   spinner.fail('Operation failed!');
// }

// For demonstration purposes in this script:
console.log(chalk.yellow('→ Simulating async operation with spinner...'));
console.log(chalk.green('✓ Async operation completed!'));

// Enhanced status display with styled formatting
console.log('');
console.log(chalk.bold('ENHANCED STATUS INFORMATION:'));

// Create a simple bordered box manually to avoid boxen import issues
const statusContent =
    '  ' + chalk.bold.blue('Application: ') + chalk.white('CLI Beautifier Example') + '\n' +
    '  ' + chalk.bold.green('Status: ') + chalk.green('✓ Running') + '\n' +
    '  ' + chalk.bold.yellow('Version: ') + chalk.yellow('1.0.0') + '\n' +
    '  ' + chalk.bold.cyan('Uptime: ') + chalk.cyan('00:00:05') + '\n' +
    '  ' + chalk.bold.magenta('Tasks: ') + chalk.magenta('5/5 completed');

const lines = statusContent.split('\n').filter(line => line.trim() !== ''); // Remove empty lines
const maxWidth = Math.max(...lines.map(line => line.replace(/\x1B\[[0-9;]*m/g, '').length)) + 4; // Add padding and account for ANSI codes

console.log(chalk.gray('  ╔' + '═'.repeat(maxWidth - 2) + '╗'));
lines.forEach(line => {
    if (line.trim() !== '') { // Only process non-empty lines
        const cleanLineLength = line.replace(/\x1B\[[0-9;]*m/g, '').length;
        const padding = Math.max(0, maxWidth - cleanLineLength - 2); // Ensure padding is not negative
        const paddedLine = line + ' '.repeat(padding);
        console.log(chalk.gray('  ║') + paddedLine + chalk.gray('║'));
    }
});
console.log(chalk.gray('  ╚' + '═'.repeat(maxWidth - 2) + '╝'));

// Enhanced task list with better visual hierarchy
console.log('');
console.log(chalk.bold('ENHANCED TASK LIST:'));

const tasks = [
    { number: 1, title: 'Initialize CLI beautifier skill', status: '✓', color: 'green' },
    { number: 2, title: 'Test basic functionality', status: '✓', color: 'green' },
    { number: 3, title: 'Verify table output', status: '✓', color: 'green' },
    { number: 4, title: 'Check progress indicators', status: '✓', color: 'green' },
    { number: 5, title: 'Validate status display', status: '✓', color: 'green' }
];

tasks.forEach(task => {
    const colorFunction = {
        green: chalk.green,
        yellow: chalk.yellow,
        red: chalk.red
    }[task.color] || chalk.white;

    console.log(
        chalk.bold(`  ${task.number}. `) +
        colorFunction(`${task.status} ${task.title}`)
    );
});

console.log('');
console.log(chalk.bold.green('✓ All tasks completed successfully!'));

// Enhanced content container using manual border
console.log('');
console.log(chalk.bold('ENHANCED CONTENT CONTAINER:'));

const contentText = [
    chalk.bold.white('This is content in an enhanced container'),
    chalk.cyan('Multiple lines work too'),
    chalk.green('Enhanced CLI functionality is working'),
    chalk.yellow('Visual improvements applied successfully')
];

const contentWidth = Math.max(...contentText.map(line => line.replace(/\x1B\[[0-9;]*m/g, '').length)) + 4; // Account for padding and remove ANSI codes for length calculation

console.log(chalk.magenta('╔' + '═'.repeat(contentWidth) + '╗'));
contentText.forEach(line => {
    const cleanLineLength = line.replace(/\x1B\[[0-9;]*m/g, '').length;
    const padding = contentWidth - cleanLineLength - 2;
    const leftPad = Math.floor(padding / 2);
    const rightPad = padding - leftPad;
    console.log(chalk.magenta('║') + ' '.repeat(leftPad) + line + ' '.repeat(rightPad) + chalk.magenta('║'));
});
console.log(chalk.magenta('╚' + '═'.repeat(contentWidth) + '╝'));

// Enhanced completion message
console.log('');

const completionText = [
    chalk.bold.green('CLI BEAUTIFIER COMPLETE EXAMPLE!'),
    chalk.bold.white('All functionality demonstrated and ready for use.')
];

const completionWidth = Math.max(...completionText.map(line => line.replace(/\x1B\[[0-9;]*m/g, '').length)) + 4;

console.log(chalk.green('╔' + '═'.repeat(completionWidth) + '╗'));
completionText.forEach(line => {
    const cleanLineLength = line.replace(/\x1B\[[0-9;]*m/g, '').length;
    const padding = completionWidth - cleanLineLength - 2;
    const leftPad = Math.floor(padding / 2);
    const rightPad = padding - leftPad;
    console.log(chalk.green('║') + ' '.repeat(leftPad) + line + ' '.repeat(rightPad) + chalk.green('║'));
});
console.log(chalk.green('╚' + '═'.repeat(completionWidth) + '╝'));

console.log('');
console.log(chalk.bold('TROUBLESHOOTING TIPS:'));
console.log('• If boxen fails to import, use manual border drawing as shown above');
console.log('• If ora fails to import, use simple status messages as alternatives');
console.log('• Always install all dependencies: npm install chalk cli-table3 cli-progress boxen ora');