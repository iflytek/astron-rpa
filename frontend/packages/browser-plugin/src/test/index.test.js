/** @format */
import { expect, test } from 'vitest';
import { Utils } from '../background/utils';


const { stringToRegex, removeUrlParams,  } = Utils;


test('stringToRegex', () => {
  expect(stringToRegex('hello')).toStrictEqual(/hello/);
});

// 测试数字匹配 /\\d/
test('stringToRegex with number', () => {
  const regex = stringToRegex('/\\d/');
  expect(regex.test('123')).toBe(true);
  expect(stringToRegex('/\\d/').source).toStrictEqual(/\d/.source);
  expect(stringToRegex('/\\d/').flags).toStrictEqual(/\d/.flags);
})

// 测试 /abc/gi
test('stringToRegex with flags', () => {
  const regex = stringToRegex('/abc/g');
  expect(regex.test('abc')).toBe(true);
  expect(regex.test('ABC')).toBe(false);
  expect(stringToRegex('/abc/g').source).toStrictEqual(/abc/g.source);
  expect(stringToRegex('/abc/g').flags).toStrictEqual(/abc/g.flags);
  expect(stringToRegex('/abc/i').test('ABC')).toBe(true);
})


test('removeUrlParams', () => {
  expect(removeUrlParams('https://www.example.com/path?param1=value1&param2??=value2')).toBe('https://www.example.com/path');
})
