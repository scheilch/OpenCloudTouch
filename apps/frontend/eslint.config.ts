import js from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";
import pluginReact from "eslint-plugin-react";

export default [
  {
    ignores: [
      "**/node_modules/**",
      "**/dist/**",
      "**/coverage/**",
      "**/tests/**",
      "**/*.test.*",
      "**/*.cy.*",
      "**/*.min.js",
      "**/*.min.css",
      "**/*.css",  // CSS files handled by stylelint, not ESLint
      "**/*.json",
      "**/*.md"
    ]
  },
  {
    files: ["**/*.{js,mjs,cjs,ts,mts,cts,jsx,tsx}"],
    plugins: {
      react: pluginReact
    },
    settings: {
      react: {
        version: "detect"
      }
    },
    languageOptions: {
      globals: globals.browser,
      parserOptions: {
        ecmaFeatures: {
          jsx: true
        }
      }
    },
    rules: {
      ...js.configs.recommended.rules,
      ...pluginReact.configs.recommended.rules,
      // React 18+ doesn't require React import in JSX files
      "react/react-in-jsx-scope": "off",
      // TypeScript migration complete - prop-types no longer needed
      "react/prop-types": "off",
      // Temporary: Disable display-name until eslint-plugin-react v8
      "react/display-name": "off"
    }
  },
  ...tseslint.configs.recommended
];
