
------------ NES - Super Mario Bros ------------

=====================
  Single Level
=====================

This environment allows you to play the original Super Mario Bros.

Environments:
    - There are 64 environments available, with the following syntax:

        SuperMarioBros-<world_number>-<level_number>-v0
         and
        SuperMarioBros-<world_number>-<level_number>-Tiles-v0

        - world_number is a number between 1 and 8
        - level_number is a number between 1 and 4

        e.g. SuperMarioBros-6-1-v0, or SuperMarioBros-3-4-Tiles-v0

Tiles vs Regular:
    - Environment with "Tiles" in their name will return a 16x13 array
      representation of the screen, where each square can have one of
      the following values:

      - 0: empty space
      - 1: object (e.g. platform, coins, flagpole, etc.)
      - 2: enemy
      - 3: Mario

    - Environment without "Tiles" will return a 256x224 array representation
      of the screen, where each square contains red, blue, and green value (RGB)

Actions:
    - The NES controller is composed of 6 buttons (Up, Left, Down, Right, A, B)
    - The step function expects an array of 0 and 1 that represents

        - First Item -  Up
        - Second Item - Left
        - Third Item -  Down
        - Fourth Item - Right
        - Fifth Item -  A
        - Sixth Item -  B

    e.g. action = [0, 0, 0, 1, 1, 0]    # [up, left, down, right, A, B]
    would activate right (4th element), and A (5th element)

    - An action of '1' represents a key down, and '0' a key up.
    - To toggle the button, you must issue a key up, then a key down.

Initiating the environment:
    - SuperMarioBros can be initiated with:

        import gym
        env = gym.make('SuperMarioBros-1-1-v0')
        env.reset()

    - fceux will be launched when reset() is called

Gameplay:
    - The game will automatically close if Mario dies or shortly after the flagpole is touched
    - The game will only accept inputs after the timer has started to decrease (i.e. it will automatically move
      through the menus and animations)
    - The total reward is the distance on the x axis.

Rendering:
    - render() will not generate a 2nd rendering, because fceux is already doing so
    - to disable this behaviour and have render() generate a separate rendering, set env.no_render = False

Variables:
    - The following variables are available in the info dict

        - distance        # Total distance from the start (x-axis)
        - life            # Number of lives Mario has (3 if Mario is alive, 0 is Mario is dead)
        - score           # The current score
        - coins           # The current number of coins
        - time            # The current time left
        - player_status   # Indicates if Mario is small (value of 0), big (value of 1), or can shoot fireballs (2+)

        - ignore          # Will be added with a value of True if the game is stuck and is terminated early

    - A value of -1 indicates that the value is unknown

Configuration:
    After creating the env, you can call env.configure() to configure some parameters.

    - lock [e.g. env.configure(lock=multiprocessing_lock)]
        SuperMario requires a multiprocessing lock when running across multiple processes, otherwise the game might get stuck

        You can either:

        1) [Preferred] Create a multiprocessing.Lock() and pass it as a parameter to the configure() method
            [e.g. env.configure(lock=multiprocessing_lock)]

        2) Create and close an environment before running your multiprocessing routine, this will create
            a singleton lock that will be cached in memory, and be used by all SuperMario environments afterwards
            [e.g. env = gym.make('SuperMarioBros-...'); env.close()]

        3) Manually wrap calls to reset() and close() in a multiprocessing.Lock()

Game is stuck:
    - In some cases, it is possible for the game to become stuck. This is likely due to a named pipe not working properly.

    - To reduce these issues, try to pass a lock to the configure method (see above), and try to reduce the number of
      running processes.

    - After 20 seconds, the stuck game will be automatically closed, and step() will return done=True with an info
      dictionary containing ignore=True. You can simply check if the ignore key is in the info dictionary, and ignore
      that specific episode.

Wrappers:
    You can use wrappers to further customize the environment. Wrappers need to be manually copied from the wrappers folder.

        theWrapperOne = WrapperOneName(init_options)
        theWrapperTwo = WrapperTwoName(init_options)
        env = gym.make('ppaquette/SuperMarioBros-1-2-v0')
        env = theWrapperTwo(theWrapperOne((env))

    - Action space:

        You can change the action space by using the ToDiscrete or ToBox wrapper

            wrapper = ToBox()
            env = wrapper(env)

        ToDiscrete will convert the action space to a Discrete(14) action space with the relevant control.
        ToBox will convert the action space to a Box(6,) action space.

    - Control:

        You can play the game manually with the SetPlayingMode wrapper.

            wrapper = SetPlayingMode('human')
            env = wrapper(env)

        Valid options are 'human' or 'algo' (default)


=====================
  META Level
=====================

Goal: 32,000 points
    - Pass all levels

Scoring:
    - Each level score has been standardized on a scale of 0 to 1,000
    - The passing score for a level is 990 (99th percentile)
    - A bonus of 1,600 (50 * 32 levels) is given if all levels are passed
    - The score for a level is the average of the last 3 tries
    - If there has been less than 3 tries for a level, the missing tries will have a score of 0
      (e.g. if you score 1,000 on the first level on your first try, your level score will be
      (1,000 + 0 + 0) / 3 = 333.33)
    - The total score is the sum of the level scores, plus the bonus if you passed all levels.

    e.g. List of tries:

    - Level 0: 500
    - Level 0: 750
    - Level 0: 800
    - Level 0: 1,000
    - Level 1: 100
    - Level 1: 200

    Level score for level 0 = [1,000 + 800 + 750] / 3 = 850     (Average of last 3 tries)
    Level score for level 1 = [200 + 100 + 0] / 3 = 100         (Tries not completed have a score of 0)
    Level score for levels 2 to 8 = 0
    Bonus score for passing all levels = 0
    ------------------------
    Total score = 850 + 100 + 0 + 0 = 950

Changing Level:
    - To unlock the next level, you must achieve a level score (avg of last 3 tries) of at least 600
      (i.e. passing 60% of the last level)
    - There are 2 ways to change level:

    1) Manual method

        - obs, reward, is_finished, info = env.step(action)
        - if is_finished is true, you can call env.change_level(level_number) to change to an unlocked level
        - level_number is a number from 0 to 31
        - you can see
            the current level with info["level"]
            the list of level score with info["scores"],
            the list of locked levels with info["locked_levels"]
            your total score with info["total_reward"]

        e.g.
            import gym
            env = gym.make('meta-SuperMarioBros-v0')
            env.reset()
            total_score = 0
            while total_score < 32000:
                action = [0] * 6
                obs, reward, is_finished, info = env.step(action)
                env.render()
                total_score = info["total_reward"]
                if is_finished:
                    env.change_level(level_you_want)

    2) Automatic change

        - if you don't call change_level() and the level is finished, the system will automatically select the
          unlocked level with the lowest level score (which is likely to be the last unlocked level)

        e.g.
            import gym
            env = gym.make('meta-SuperMarioBros-v0')
            env.reset()
            total_score = 0
            while total_score < 32000:
                action = [0] * 6
                obs, reward, is_finished, info = env.step(action)
                env.render()
                total_score = info["total_reward"]

-----------------------------------------------------
