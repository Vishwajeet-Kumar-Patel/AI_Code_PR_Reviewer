# JavaScript Best Practices

## Modern JavaScript (ES6+)

### Variable Declarations
- Use `const` by default
- Use `let` when reassignment is needed
- Avoid `var`

```javascript
// Good
const API_KEY = 'your-key';
let counter = 0;

// Avoid
var userName = 'John';
```

### Arrow Functions
- Use arrow functions for callbacks and simple functions
- Be aware of `this` binding differences

```javascript
// Good
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(n => n * 2);

// Good for methods that need context
const obj = {
    name: 'Example',
    greet: function() {
        return `Hello, ${this.name}`;
    }
};
```

### Template Literals
- Use template literals for string interpolation
- Use for multi-line strings

```javascript
// Good
const greeting = `Hello, ${userName}!`;
const multiLine = `
    This is a
    multi-line string
`;

// Avoid
const greeting = 'Hello, ' + userName + '!';
```

### Destructuring
- Use object and array destructuring

```javascript
// Object destructuring
const { name, email } = user;

// Array destructuring
const [first, second] = array;

// Function parameters
function processUser({ name, email, age = 18 }) {
    // ...
}
```

### Spread and Rest Operators
- Use spread for copying and merging
- Use rest for function parameters

```javascript
// Spread
const newArray = [...oldArray, newItem];
const mergedObject = { ...obj1, ...obj2 };

// Rest
function sum(...numbers) {
    return numbers.reduce((acc, n) => acc + n, 0);
}
```

## Async Programming

### Promises
- Use promises for asynchronous operations
- Chain with `.then()` and `.catch()`

```javascript
// Good
fetchData()
    .then(data => processData(data))
    .then(result => console.log(result))
    .catch(error => console.error(error));
```

### Async/Await
- Prefer async/await for cleaner async code
- Always handle errors with try/catch

```javascript
// Good
async function fetchUserData(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Failed to fetch user:', error);
        throw error;
    }
}
```

## Error Handling

### Try/Catch
- Use try/catch for synchronous errors
- Handle async errors properly

```javascript
// Synchronous
try {
    const result = JSON.parse(jsonString);
    processResult(result);
} catch (error) {
    console.error('Invalid JSON:', error);
}

// Asynchronous
async function safeOperation() {
    try {
        await riskyOperation();
    } catch (error) {
        console.error('Operation failed:', error);
        // Handle error appropriately
    }
}
```

### Custom Errors
- Create custom error classes

```javascript
class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = 'ValidationError';
    }
}

throw new ValidationError('Invalid input');
```

## Functions

### Pure Functions
- Write pure functions when possible
- Avoid side effects

```javascript
// Good - pure function
function add(a, b) {
    return a + b;
}

// Avoid - side effects
let total = 0;
function addToTotal(value) {
    total += value;  // Side effect
}
```

### Default Parameters
- Use default parameters

```javascript
function greet(name = 'Guest', greeting = 'Hello') {
    return `${greeting}, ${name}!`;
}
```

### Function Documentation
- Use JSDoc for documentation

```javascript
/**
 * Calculate the total price including tax
 * @param {number} price - The base price
 * @param {number} taxRate - The tax rate (default 0.1)
 * @returns {number} The total price with tax
 */
function calculateTotal(price, taxRate = 0.1) {
    return price * (1 + taxRate);
}
```

## Arrays and Objects

### Array Methods
- Use functional array methods

```javascript
// Map
const doubled = numbers.map(n => n * 2);

// Filter
const evens = numbers.filter(n => n % 2 === 0);

// Reduce
const sum = numbers.reduce((acc, n) => acc + n, 0);

// Find
const user = users.find(u => u.id === targetId);

// Some and Every
const hasAdult = users.some(u => u.age >= 18);
const allAdults = users.every(u => u.age >= 18);
```

### Object Methods
- Use Object methods for manipulation

```javascript
// Keys, values, entries
const keys = Object.keys(obj);
const values = Object.values(obj);
const entries = Object.entries(obj);

// Assign (shallow copy)
const copy = Object.assign({}, original);

// Freeze (immutability)
Object.freeze(config);
```

## Security Best Practices

### XSS Prevention
- Never use innerHTML with user input
- Sanitize user input
- Use textContent for text

```javascript
// Avoid
element.innerHTML = userInput;

// Good
element.textContent = userInput;

// Or use a sanitization library
element.innerHTML = DOMPurify.sanitize(userInput);
```

### Avoid eval()
- Never use eval() with user input
- Use JSON.parse() for JSON strings

```javascript
// Avoid
eval(userCode);

// Good
const data = JSON.parse(jsonString);
```

### Secure Random
- Use crypto API for security-sensitive random values

```javascript
// Good for security
const array = new Uint32Array(10);
crypto.getRandomValues(array);

// Avoid for security
Math.random();  // Not cryptographically secure
```

## Module System

### ES6 Modules
- Use ES6 import/export
- Named exports for utilities
- Default exports for main functionality

```javascript
// Export
export const helper = () => { };
export default class Main { }

// Import
import Main from './Main';
import { helper } from './utils';
```

## Code Quality

### Linting
- Use ESLint
- Configure rules for your project
- Use Prettier for formatting

### Type Checking
- Consider TypeScript for large projects
- Or use JSDoc with type checking

## Performance

### Avoid Memory Leaks
- Remove event listeners when not needed
- Cancel pending requests on unmount
- Clean up timers and intervals

```javascript
// Good
const controller = new AbortController();
fetch(url, { signal: controller.signal });

// Later: cancel request
controller.abort();

// Clean up event listeners
element.addEventListener('click', handler);
// Later
element.removeEventListener('click', handler);
```

### Debouncing and Throttling
- Use debounce for search inputs
- Use throttle for scroll handlers

```javascript
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}
```

## Testing

### Unit Tests
- Write tests for pure functions
- Mock external dependencies
- Use Jest or similar frameworks

```javascript
describe('calculateTotal', () => {
    test('calculates with default tax rate', () => {
        expect(calculateTotal(100)).toBe(110);
    });
    
    test('calculates with custom tax rate', () => {
        expect(calculateTotal(100, 0.2)).toBe(120);
    });
});
```

## Best Practices Summary

1. Use modern ES6+ features
2. Write pure functions when possible
3. Handle errors properly
4. Avoid global variables
5. Use const by default
6. Prefer async/await over callbacks
7. Validate and sanitize user input
8. Write tests for critical code
9. Use a linter and formatter
10. Document your code
