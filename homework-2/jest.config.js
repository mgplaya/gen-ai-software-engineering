module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests'],
  testMatch: ['**/tests/test_*.spec.ts'],
  setupFiles: ['<rootDir>/tests/jest.setup.ts'],
  collectCoverageFrom: ['src/**/*.ts', '!src/main.ts'],
  coverageThreshold: {
    global: { branches: 85, functions: 85, lines: 85, statements: 85 },
  },
  testTimeout: 30000,
};
