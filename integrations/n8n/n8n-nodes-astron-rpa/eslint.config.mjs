import ts from "typescript-eslint";
export default ts.config(
  { ignores: ["dist/**", "node_modules/**"] },
  ...ts.configs.recommended,
  {
    files: ["tests/**/*.cjs"],
    rules: { "@typescript-eslint/no-require-imports": "off" },
  },
);
