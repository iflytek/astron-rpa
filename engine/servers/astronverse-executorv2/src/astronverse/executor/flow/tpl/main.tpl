from {{MAIN_PROCESS_NAME}} import main

if __name__ == '__main__':
    kwargs = globals().get('_kwargs', {})
    main(**kwargs)
