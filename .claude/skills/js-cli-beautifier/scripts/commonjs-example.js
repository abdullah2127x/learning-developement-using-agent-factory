// Example demonstrating proper CommonJS usage for CLI beautification
// This script shows the correct way to import and use CLI beautification libraries
// with CommonJS to avoid "is not a function" errors

const chalk = require('chalk');
const boxen = require('boxen');
const ora = require('ora');

// Create a spinner for loading states
const spinner = ora({
  text: chalk.blue('Application starting...'),
  spinner: 'clock'
});
spinner.start();

// Simulate loading steps with enhanced visual feedback
setTimeout(() => {
  spinner.text = chalk.blue('Loading configuration...');
}, 500);

setTimeout(() => {
  spinner.text = chalk.blue('Connecting to database...');
}, 1000);

setTimeout(() => {
  spinner.succeed(chalk.green('Database connection established'));
  console.log(chalk.blue('┌─────────────────────────────────────────┐'));
  console.log(chalk.blue('│  ') + chalk.bold('Starting server on port 3000') + chalk.blue('         │'));
  console.log(chalk.blue('└─────────────────────────────────────────┘'));
}, 1500);

setTimeout(() => {
  console.log(chalk.green('✓ ') + chalk.bold.green('Server running and listening for requests'));
  console.log(chalk.cyan('ℹ ') + chalk.bold.cyan('User authentication service initialized'));
}, 2000);

setTimeout(() => {
  console.log(chalk.yellow('⚠ ') + chalk.bold.yellow('API endpoints registered'));
  console.log(chalk.green('✓ ') + chalk.bold.green('Caching system activated'));
}, 2500);

setTimeout(() => {
  console.log(boxen(chalk.bold.green('Application ready for use'), {
    padding: 1,
    margin: 1,
    borderStyle: 'round',
    borderColor: 'green',
    backgroundColor: '#555555'
  }));
}, 3000);

setTimeout(() => {
  // System status table using colors
  console.log(chalk.bold('System Status:'));
  console.log(chalk.blue('┌─────────────────────────────────────────┐'));
  console.log(chalk.blue('│ ') + chalk.bold('Metric') + '           ' + chalk.bold('Value') + chalk.blue('                │'));
  console.log(chalk.blue('├─────────────────────────────────────────┤'));
  console.log(chalk.blue('│ ') + chalk.cyan('Memory usage: ') + chalk.yellow('45MB') + chalk.blue('                     │'));
  console.log(chalk.blue('│ ') + chalk.cyan('Active connections: ') + chalk.yellow('12') + chalk.blue('                 │'));
  console.log(chalk.blue('│ ') + chalk.cyan('Processing queue: ') + chalk.yellow('0') + chalk.blue('                    │'));
  console.log(chalk.blue('└─────────────────────────────────────────┘'));
}, 3500);

setTimeout(() => {
  console.log(chalk.bold.green('✓ Health check passed'));
  console.log(chalk.bold.blue('Ready to handle requests'));
}, 4000);

// Additional logging with different log levels and colors
setTimeout(() => {
  console.log(chalk.bgBlue.black(' INFO ') + ' ' + chalk.blue('All systems operational'));
}, 4500);

setTimeout(() => {
  console.log(chalk.bgYellow.black(' WARN ') + ' ' + chalk.yellow('High memory usage detected'));
}, 5000);

setTimeout(() => {
  console.log(chalk.bgRed.black(' ERROR ') + ' ' + chalk.red('Failed to connect to external service'));
}, 5500);

setTimeout(() => {
  console.log(chalk.bgGray.black(' DEBUG ') + ' ' + chalk.gray('Processing request from user ID 12345'));
}, 6000);

// Logging objects and arrays with enhanced formatting
setTimeout(() => {
  const user = {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com',
    role: 'admin'
  };

  const tasks = ['task1', 'task2', 'task3'];

  console.log(chalk.bold('Current User Information:'));
  console.log(chalk.blue('┌─────────────────────────────────────────┐'));
  console.log(chalk.blue('│ ') + chalk.bold('ID: ') + chalk.yellow(user.id) + chalk.blue('                                │'));
  console.log(chalk.blue('│ ') + chalk.bold('Name: ') + chalk.yellow(user.name) + chalk.blue('                            │'));
  console.log(chalk.blue('│ ') + chalk.bold('Email: ') + chalk.yellow(user.email) + chalk.blue('                         │'));
  console.log(chalk.blue('│ ') + chalk.bold('Role: ') + chalk.yellow(user.role) + chalk.blue('                            │'));
  console.log(chalk.blue('└─────────────────────────────────────────┘'));

  console.log(chalk.bold('Pending Tasks:'));
  tasks.forEach((task, index) => {
    console.log(chalk.green(`  ${index + 1}. [ ] `) + chalk.white(task));
  });

  // Final success message
  setTimeout(() => {
    console.log(boxen(chalk.bold.green('✓ Application initialized successfully'), {
      padding: 1,
      margin: 1,
      borderStyle: 'double',
      borderColor: 'green',
      backgroundColor: '#005500'
    }));
  }, 1000);
}, 6500);