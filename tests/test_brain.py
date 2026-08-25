from core.brain import get_mirai_state


def test_brain():

    state = get_mirai_state()


    print("\n====================")
    print("MIRAI BRAIN STATE")
    print("====================")


    for system, data in state.items():

        print("\nSYSTEM:", system)

        print(data)



if __name__ == "__main__":

    test_brain()