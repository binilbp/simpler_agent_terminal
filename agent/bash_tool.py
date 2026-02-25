import subprocess
import os
from typing import Dict
from langchain_core.tools import tool
from config.settings import SETTINGS



class Bash:

    def __init__(self):
        # set the cwd to default_dir and get the banned command list
        self.cwd = SETTINGS.default_dir
        self.ban_list = SETTINGS.banned_commands


    # check befor executing
    def exec_bash_command(self, cmd: str) -> Dict[str, str]:
        base_cmd = cmd.split()[0]

        # prevent banned command from running
        if base_cmd in self.ban_list:
            return {"error": f"Command '{base_cmd}' is not allowed to run by the user"}
        return self._run_bash_command(cmd)


    def _run_bash_command(self, cmd: str) -> Dict[str, str]:
        try:
            wrapped = f"{cmd}; echo '__END__'; pwd"
            result = subprocess.run(
                wrapped, shell=True, cwd=self.cwd, capture_output=True, text=True, executable="/bin/bash"
            )
            stdout = result.stdout
            if "__END__" in stdout:
                parts = stdout.split("__END__")
                output = parts[0].strip()
                new_cwd = parts[1].strip()
                if os.path.isdir(new_cwd):
                    self.cwd = new_cwd
                    # also update the TUI 
                    update_TUI_dir(self.cwd)
            else:
                output = stdout
            return {"stdout": output, "stderr": result.stderr, "cwd": self.cwd}

        except Exception as e:
            return {"error": str(e)}


bash_core = Bash()


@tool
def bash_tool(cmd: str) -> str:
    """Execute bash command. Input should be the exact command string."""
    result = bash_core.exec_bash_command(cmd)
    if 'error' in result and result.get('error'):
        return f"Error: {result.get['error']}"
    return f"STDOUT:\n{result['stdout']}\nSTDERR:\n{result['stderr']}\nCWD:\n{result['cwd']}"






