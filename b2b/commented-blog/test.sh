#!/bin/bash
rm -rf deploy/ && hyde gen && find deploy && git diff deploy/ && echo -e '\033[32mTEST PASSED\033[0m' || echo -e '\033[31mTEST FAILED\033[0m'
