from {{MAIN_PROCESS_NAME}} import main

if __name__ == '__main__':
    _args = globals().get('_args', {})
    main(_args)
