#!/bin/bash
rm -rf deploy/ && hyde -v gen && find deploy && git diff . && echo -e '\033[32mTEST PASSED\033[0m' || echo -e '\033[31mTEST FAILED\033[0m'
