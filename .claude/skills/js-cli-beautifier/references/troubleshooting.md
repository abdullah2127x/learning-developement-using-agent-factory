# Troubleshooting CLI Beautification

This document covers common issues encountered when implementing CLI beautification and their solutions.

## Module Import Issues

### Boxen Module Issues
**Problem**: `TypeError: boxen is not a function`

**Solution**: Use the correct import method:
```javascript
// Correct
const boxen = require('boxen');

// Incorrect
const { boxen } = require('boxen');
```

### Ora Module Issues
**Problem**: `TypeError: ora is not a function`

**Solution**: Use the correct import method:
```javascript
// Correct
const ora = require('ora');

// Usage in async context
async function example() {
  const spinner = ora('Loading...').start();
  try {
    await someAsyncOperation();
    spinner.succeed('Success!');
  } catch (error) {
    spinner.fail('Failed!');
  }
}
```

## Fallback Implementations

When modules fail to load, you can implement similar functionality manually:

### Manual Box Implementation
```javascript
function createBox(content, options = {}) {
  const lines = content.split('\n');
  const maxWidth = Math.max(...lines.map(line => line.replace(/\x1B\[[0-9;]*m/g, '').length)) + 4;

  let result = '╔' + '═'.repeat(maxWidth) + '╗\n';
  lines.forEach(line => {
    const cleanLineLength = line.replace(/\x1B\[[0-9;]*m/g, '').length;
    const padding = Math.max(0, maxWidth - cleanLineLength - 2);
    const paddedLine = line + ' '.repeat(padding);
    result += '║' + paddedLine + '║\n';
  });
  result += '╚' + '═'.repeat(maxWidth) + '╝';

  return result;
}
```

### Manual Progress Implementation
```javascript
function simpleProgressBar(current, total, options = {}) {
  const percentage = Math.round((current / total) * 100);
  const barLength = 20;
  const filledLength = Math.round((current / total) * barLength);
  const bar = '█'.repeat(filledLength) + '░'.repeat(barLength - filledLength);

  return `Progress: |${bar}| ${percentage}% (${current}/${total})`;
}
```

## Dependency Management

### Installing Dependencies
```bash
npm install chalk cli-table3 cli-progress ora boxen inquirer
```

### Package.json Example
```json
{
  "dependencies": {
    "chalk": "^4.1.2",
    "cli-table3": "^0.6.3",
    "cli-progress": "^3.12.0",
    "ora": "^8.0.0",
    "boxen": "^7.0.0",
    "inquirer": "^8.2.5"
  }
}
```

## Cross-Platform Compatibility

### Terminal Compatibility Issues
- Some terminals don't support certain Unicode characters
- Colors may not display in all environments
- Consider using `supports-color` package to detect color support

### Testing in Different Environments
- Test in various terminals (bash, zsh, Windows cmd, PowerShell)
- Consider fallbacks for environments with limited feature support
- Use feature detection rather than assuming capabilities