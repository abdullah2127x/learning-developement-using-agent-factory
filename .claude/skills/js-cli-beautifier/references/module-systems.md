# CommonJS vs ES Modules for CLI Beautification Libraries

This guide explains the differences between CommonJS and ES modules when using CLI beautification libraries, and how to properly configure your project to avoid import errors.

## Overview

Modern CLI beautification libraries like `ora`, `boxen`, `chalk`, etc., support both CommonJS and ES modules, but the import syntax differs. Understanding these differences is crucial to avoid runtime errors like "is not a function".

## CommonJS (require) vs ES Modules (import)

### CommonJS Pattern
```javascript
// Using require() - traditional Node.js approach
const chalk = require('chalk');
const boxen = require('boxen');
const ora = require('ora');
```

### ES Modules Pattern
```javascript
// Using import - modern approach
import chalk from 'chalk';
import boxen from 'boxen';
import ora from 'ora';
```

## Project Configuration

### CommonJS Configuration
- Default Node.js module system
- Uses `.js` file extension
- No special configuration needed in package.json
- Compatible with older Node.js versions

### ES Modules Configuration
- Modern module system
- Requires `"type": "module"` in package.json
- Uses `.js` or `.mjs` file extensions
- Requires Node.js 12+ for full support

## Common Import Errors and Solutions

### Error: "ora is not a function" or "boxen is not a function"
**Cause**: Mixing import systems or using incorrect syntax
**Solution**:
- For CommonJS: `const ora = require('ora')`
- For ES modules: `import ora from 'ora'`

### Error: "Cannot use import statement outside a module"
**Cause**: Using import syntax without ES modules enabled
**Solution**: Add `"type": "module"` to package.json

### Error: "require is not defined"
**Cause**: Using CommonJS syntax in ES modules environment
**Solution**: Use import syntax instead, or remove `"type": "module"` from package.json

## Best Practices

1. **Consistency**: Stick to one module system throughout your project
2. **Documentation**: Clearly document which module system your project uses
3. **Configuration**: Update package.json appropriately for your chosen module system
4. **Testing**: Test your imports work correctly before building complex features

## Migration Tips

### From CommonJS to ES Modules
1. Add `"type": "module"` to package.json
2. Replace `require()` statements with `import` statements
3. Update file extensions if needed (or keep .js with proper package.json config)
4. Test all imports to ensure they work correctly

### From ES Modules to CommonJS
1. Remove `"type": "module"` from package.json (or set to "commonjs")
2. Replace `import` statements with `require()` statements
3. Update file extensions if needed
4. Test all imports to ensure they work correctly