#!/usr/bin/env python3

import os, sys, argparse
from time import time
from subprocess import check_call, STDOUT
from tempfile import NamedTemporaryFile

from prettytable import PrettyTable
from colorama import Fore, Style
import matplotlib.pyplot as plt


with open("./src/rounds.txt", "r") as f:
    ROUNDS = int(f.read())



SLOW_LANGUAGES = {
    "Python": "python3 main.py",
    "C++": "g++ main.cpp -o main && ./main",
    "JavaScript": "node main.js",
    "TypeScript": "deno run --allow-read --allow-hrtime main.ts",
    "Java": "javac main.java && java main",
}


FAST_LANGUAGES = {
    "Python": "pypy3 main.py",
}



SLOW_CHANGED_LANGUAGES = SLOW_LANGUAGES.copy()
FAST_CHANGED_LANGUAGES = FAST_LANGUAGES.copy()


SLOW_LANGUAGES_RESULTS = {}
FAST_LANGUAGES_RESULTS = {}


def cleanup() -> None:
    pass


def change_round() -> None:
    with open("./src/rounds.txt", "w") as f:
        f.write(str(ROUNDS))


#possibly remove most of this cauz it's kinda not needed
def name_to_abbr(reverse: bool = True, entry_languages: dict[str, str] | list[str] = SLOW_CHANGED_LANGUAGES, capitalize: bool = False, single: bool = False, single_name: str = "") -> dict[str, str] | list[str]:

    if single:
        match single_name:
            case "Csharp":
                return "C#"
            case "Cpp":
                return "C++"
            case "Js" | "Node":
                return "JavaScript"
            case "Ts" | "Deno":
                return "TypeScript"
            case _:
                return single_name



    if not entry_languages:
        entry_languages = SLOW_LANGUAGES.copy()
    languages_type = type(entry_languages)
    #checking if dict and if so convert to list
    if languages_type == dict:
        languages_values = entry_languages.values()
        entry_languages = entry_languages.keys()


    new_languages = []
    #abbreviation to normal
    if reverse:
        for language in entry_languages:
            match language.lower():
                case "c#":
                    new_languages.append("csharp")
                case "c++":
                    new_languages.append("cpp")
                case _:
                    new_languages.append(language.lower())


    #normal to abbreviation
    else:
        for language in entry_languages:
            match language.lower():
                case "csharp":
                    new_languages.append("c#")
                case "cpp":
                    new_languages.append("c++")
                case _:
                    new_languages.append(language.lower())


    if capitalize:
        new_languages = [language.capitalize() for language in new_languages]




    if languages_type == dict:
        return_languages = {}
        #for value in languages_values:
            #for language in new_languages:
                #return_languages[language] = value
                #print(return_languages)
        #return return_languages
        for language, value in zip(new_languages, languages_values):
            return_languages[language] = value
        return return_languages


    return new_languages












#TODO maybe put the check_call in a subfunction
def call_languages(MODE: str) -> None:
    global languages_output
    return_times = {}
    #normal
    if MODE in ["both", "slow", "unoptimized"]:
        languages = name_to_abbr()
        slow_start = time() 
        for language, command in languages.items():
            #fast asf refer: https://stackoverflow.com/questions/13835055/python-subprocess-check-output-much-slower-then-call
            with NamedTemporaryFile() as f:
                #TODO remove shell=True and the extra sh
                check_call(f'/usr/bin/time -f " %e %P %M" sh -c  "{command}" ', shell=True, stdout=f, stderr=STDOUT, cwd="./src/" + language + "/slow")
                f.seek(0)
                output = f.read().decode("utf8").split()
                #for docker
                #if language == "typescript":
                    #del output[0]; del output[0]
                #get the compilation time 
                total_time = float(output[2])
                output[2] = float(output[2]) - float(output[1])
                output.append(total_time)
            SLOW_LANGUAGES_RESULTS[language] = output

        slow_end = time() - slow_start
        return_times["slow"] = slow_end

    if MODE in ["both", "fast", "optimized"]:
        languages = name_to_abbr(entry_languages=FAST_CHANGED_LANGUAGES)
        fast_start = time()
        for language, command in languages.items():

            #fast asf refer: https://stackoverflow.com/questions/13835055/python-subprocess-check-output-much-slower-then-call
            with NamedTemporaryFile() as f:
                #TODO remove shell=True and the extra sh
                check_call(f'/usr/bin/time -f " %e %P %M" sh -c  "{command}" ', shell=True, stdout=f, stderr=STDOUT, cwd="./src/" + language + "/fast")
                f.seek(0)
                output = f.read().decode("utf8").split()
                #for docker
                if language == "typescript":
                    del output[0]; del output[0]
                #get the compilation time 
                total_time = float(output[2])
                output[2] = float(output[2]) - float(output[1])
                output.append(total_time)
            FAST_LANGUAGES_RESULTS[language] = output

        fast_end = time() - fast_start
        return_times["fast"] = fast_end

    return return_times








def clear() -> None:
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def arg_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Calculate the prime numbers between any given range.")
    parser.add_argument("-c", "--custom", help="Enter a custom rounds value.", type=int)
    parser.add_argument("-n", "--nogui", help="Use this if you don't want to use graphical graphs.", action="store_true")
    args = parser.parse_args()
    return args




def table_and_graph(total_time: float, nogui: bool, MODE: str, times: list[float]) -> None:


    def graph(languages_array: list) -> None:

        x = name_to_abbr(False, list(languages_array.keys()), True)
        y = []
        xlabels = "Languages"
        ylabels = ["Times (s)", "Time (s)", "Time (s)", "Memory (kB)"]
        titles = ["Total time per language", "Execution time per language", "Compilation/Interpretation time per language", "Memory usage per language"]




        total_time_language = list(map(lambda x: round(x[:][-1], 3), list(SLOW_LANGUAGES_RESULTS.values())))
        y.append(total_time_language)   

        execution_time_language = list(map(lambda x: round(float(x[:][1]), 3), list(SLOW_LANGUAGES_RESULTS.values()))) 
        y.append(execution_time_language)   

        compilation_time_language = list(map(lambda x: round(float(x[:][2]), 3), list(SLOW_LANGUAGES_RESULTS.values())))
        y.append(compilation_time_language)   

        memory_language = list(map(lambda x: int(x[:][4]), list(SLOW_LANGUAGES_RESULTS.values())))
        y.append(memory_language)   
        for index, _y in enumerate(y):
            xlabel = xlabels[index]
            ylabel = ylabels[index]
            title = titles[index]
            i = index; i += 1
            
            plt.subplot(2, 2, i)
            plt.bar(x, _y)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.title(title)
            plt.grid()
    

    def table(results_list: list, total_times: float) -> None:
        
        my_table = PrettyTable([
            Fore.RED + "Language" + Fore.RESET,
            Fore.GREEN + "Total time (s)" + Fore.RESET,
            Fore.BLUE + "Execution time (s)" + Fore.RESET,
            Fore.CYAN + "Compilation / Interpretation time (s)" + Fore.RESET,
            Fore.LIGHTGREEN_EX + "Peak Memory usage (kB)" + Fore.RESET,
            Fore.MAGENTA + "Version" + Fore.RESET,
        ])


        total_execution_time = 0
        total_compilation_time = 0
        total_memory_usage = 0

        for language, output in name_to_abbr(False, results_list, True).items():
            for result in output:
                if result is output[1]:
                    total_execution_time += float(result)
                elif result is output[2]:
                    total_compilation_time += float(result)
                elif result is output[4]:
                    total_memory_usage += int(result)
            
            my_table.add_row([
                language,
                round(float(output[-1]), 3),#total time
                round(float(output[1]), 3), #execution time
                round(float(output[2]), 3), #compilation time
                output[4], #memory usage
                output[0]  #version
            ])
        
        my_table.add_row([
            Fore.RED + f"Total ({len(results_list)})" + Fore.RESET, #total languages
            Fore.GREEN + str(round(total_times, 3)) + Fore.RESET, #sum of all total times 
            Fore.BLUE + str(round(total_execution_time, 3)) + Fore.RESET, #sum of all execution times
            Fore.CYAN + str(round(total_compilation_time, 3)) + Fore.RESET, #sum of all compilation times
            Fore.LIGHTGREEN_EX + str(total_memory_usage) + Fore.RESET, #sum of all peak memory usages
            Fore.MAGENTA + "####" + Fore.RESET ####
        ])

        print(my_table)

    if MODE in ["both", "slow", "unoptimized"]:
        table(SLOW_LANGUAGES_RESULTS, times["slow"])
        #graphs
        if not nogui:

            graph(SLOW_LANGUAGES_RESULTS)

            plt.suptitle("Graphs")
            plt.get_current_fig_manager().set_window_title("Results")
            plt.show()
            #save graphs
            #plt.savefig(fname="./results/graphs.png")

    if MODE in ["both", "fast", "optimized"]:
        table(FAST_LANGUAGES_RESULTS, times["fast"])

        if not nogui:
            graph(FAST_LANGUAGES_RESULTS)
            plt.suptitle("Graphs")
            plt.get_current_fig_manager().set_window_title("Results")
            plt.show()
            #save graphs
            #plt.savefig(fname="./results/graphs.png")

    print("\nIn total this all comparison took: " + Fore.GREEN + str(round(total_time, 3)) + Fore.RESET + " seconds.")

#TODO maybe add a while loop for wrong inputs
def menu(nogui: bool) -> None:
    global ROUNDS 
    MODE = "both"
    clear()
    start_input = ""
    while (start := start_input.lower()) not in ["start", "play"] :
        if start in ["exit", "quit", "leave"]:
            raise KeyboardInterrupt
        elif start in ["options", "config"]:
            clear()
            print(f"{Fore.MAGENTA + 'Choose one of the following options to change' + Fore.RESET}:    {Fore.CYAN + '(R)ounds' + Fore.RESET}    {Fore.LIGHTBLUE_EX + '(L)anguages' + Fore.RESET}    {Fore.LIGHTYELLOW_EX+ '(M)ode' + Fore.RESET}    {Fore.LIGHTGREEN_EX + '(G)raphs' + Fore.RESET}    {Fore.RED + '(B)ack' + Fore.RESET}")
            options_input = input(f"{Fore.BLUE}options{Fore.RESET}> ")
            options_input = options_input.lower()
            #TODO add options to languages and graphs
            #rounds
            if options_input in ["rounds", "round", "r"]:
                
                clear()
                print("The current Rounds are set to: " + Fore.LIGHTCYAN_EX + str(ROUNDS) + Fore.RESET)
                print("Type the rounds you want to change to!")
                rounds_input = input(f"{Fore.BLUE}options{Fore.RESET}/{Fore.CYAN}rounds{Fore.RESET}> ")
                if rounds_input.isdigit():
                    ROUNDS = int(rounds_input)
                    print(f"{Fore.GREEN}Rounds set to {ROUNDS}." + Fore.RESET)
                else:
                    print(f"{Fore.LIGHTRED_EX}Invalid rounds value." + Fore.RESET) 
            

            elif options_input in ["mode", "m"]:
                clear()
                print("The current Mode is set to: " + Fore.LIGHTMAGENTA_EX + MODE.capitalize() + Fore.RESET)
                print("Type the mode you want to change to (both, optimized or unoptimized)!")
                mode_input = input(f"{Fore.BLUE}options{Fore.RESET}/{Fore.LIGHTYELLOW_EX}mode{Fore.RESET}> ")
                if mode_input.lower() in ["fast", "optimized"]:
                    MODE = "fast" 
                    print(f"{Fore.GREEN}Mode set to {MODE}." + Fore.RESET)
                elif mode_input.lower() in ["slow", "unoptimized"]:
                    MODE = "slow"
                    print(f"{Fore.GREEN}Mode set to {MODE}." + Fore.RESET)

                else:
                    print(f"{Fore.LIGHTRED_EX}Invalid mode value." + Fore.RESET)


            elif options_input in ["language", "languages", "l"]:
                clear()
                #if no changed languages show all
                if SLOW_CHANGED_LANGUAGES == SLOW_LANGUAGES:
                    print("The current Languages are set to: " + Fore.LIGHTCYAN_EX + ", ".join(map(str, SLOW_LANGUAGES.keys())) + Fore.RESET)
                
                else: #if changed languages show changed and available
                    print("The current Languages are set to: " + Fore.LIGHTCYAN_EX + ", ".join(map(str, SLOW_CHANGED_LANGUAGES)) + Fore.RESET)
                    print("The available Languages are set to: " + Fore.LIGHTMAGENTA_EX + ", ".join(map(str, SLOW_LANGUAGES.keys())) + Fore.RESET)

                print(f"Type the languages you want to change to! Split them with a comma, and prefix the language with {Fore.MAGENTA}'?'{Fore.RESET} to remove it.")
                languages_input = input(f"{Fore.BLUE}options{Fore.RESET}/{Fore.LIGHTBLUE_EX}languages{Fore.RESET}> ").replace(" " , "").split(",")
                for language_input in languages_input:
                    try:




                        if (capitalized_language := name_to_abbr(single=True, single_name=language_input.lower().capitalize())) in SLOW_LANGUAGES.keys():
                            #SLOW_CHANGED_LANGUAGES.clear()
                            SLOW_CHANGED_LANGUAGES[capitalized_language] = SLOW_LANGUAGES[capitalized_language]
                            #TODO remove this shitty if statement when all the optimized version are added
                            if capitalized_language in FAST_LANGUAGES_RESULTS.keys():
                                FAST_CHANGED_LANGUAGES[capitalized_language] = FAST_LANGUAGES[capitalized_language]

                            print(f"{Fore.GREEN}Language {capitalized_language} added." + Fore.RESET)

                        elif language_input[0] == "?":
                            language_name = language_input[1:].lower().capitalize()
                            language_name = name_to_abbr(single=True, single_name=language_name)
                            if language_name in SLOW_CHANGED_LANGUAGES.keys():
                                SLOW_CHANGED_LANGUAGES.pop(language_name)
                                #TODO remove this shitty if statement when all the optimized version are added
                                if language_name in FAST_LANGUAGES.keys():
                                    FAST_CHANGED_LANGUAGES.pop(language_name)

                                print(f"{Fore.MAGENTA}Language {language_name} removed." + Fore.RESET)
                            else:
                                print(f"{Fore.LIGHTRED_EX}Language {language_name} not found." + Fore.RESET) 

                        else:
                            print(f"{Fore.LIGHTRED_EX}Language {language_input} not found." + Fore.RESET)

                    except IndexError:
                        print(Fore.LIGHTRED_EX + "Invalid language." + Fore.RESET) 


            elif options_input in ["graph", "graphs", "g"]:
                pass


        elif start in ["info", "information", "details"]:
            print("INFORMATIONS")



        start_input = input(
            f"Enter either {Fore.RED}'start'{Fore.RESET} to start the speed comparison, {Fore.BLUE}'options'{Fore.RESET} to change the default config, {Fore.GREEN}'info'{Fore.RESET} for the current program information or {Fore.MAGENTA}'quit'{Fore.RESET} to exit.\n->"
        )


        #if none of the above
        clear()
    change_round()
    print(f"This comparison will run to {Fore.RED + str(ROUNDS) + Fore.RESET} and it is using {Style.BRIGHT + str(len(SLOW_CHANGED_LANGUAGES.keys())) + Style.RESET_ALL} languages: {Fore.MAGENTA + ', '.join(map(str, SLOW_CHANGED_LANGUAGES.keys())) + Fore.RESET}")


    #start actual benchmark
    start_benchmark = time()
    times = call_languages(MODE)
    total_benchmark = time() - start_benchmark
    table_and_graph(total_benchmark, nogui, MODE, times)





def main() -> None:
    global ROUNDS
    args = arg_parser()
    if args.custom:
        ROUNDS = args.custom
    if args.nogui:
        nogui = True 
    else:
        nogui = False

    menu(nogui)




if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.MAGENTA + "\nBye..." + Fore.RESET)
        exit(0)
else:
    print(Fore.LIGHTRED_EX + "DIE!!!!!" + Fore.RESET)
    exit(1)
