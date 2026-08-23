import os
import subprocess
import tempfile


def execute(data: str, input_str: str, lang: str) -> dict:
    clean_lang = lang.lstrip(".").lower()
    suffix = ".py" if clean_lang in ("py", "python") else f".{clean_lang}"

    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=suffix) as f:
        f.write(data)
        filename = f.name

    try:
        if clean_lang in ("py", "python"):
            result = subprocess.run(
                ["python3", filename],
                input=input_str,
                capture_output=True,
                text=True,
                timeout=10,
            )
        elif clean_lang == "java":
            jdir = tempfile.mkdtemp()
            jfile = os.path.join(jdir, "Main.java")
            with open(jfile, "w+", encoding="utf-8") as jf:
                jf.write(data)
            subprocess.run(["javac", jfile], capture_output=True, text=True, timeout=10)
            result = subprocess.run(
                ["java", "-cp", jdir, "Main"],
                input=input_str,
                capture_output=True,
                text=True,
                timeout=10,
            )
        elif clean_lang in ("cpp", "c++"):
            out_bin = filename + ".out"
            subprocess.run(
                ["g++", filename, "-o", out_bin],
                capture_output=True,
                text=True,
                timeout=10,
            )
            result = subprocess.run(
                [out_bin],
                input=input_str,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if os.path.exists(out_bin):
                os.remove(out_bin)
        else:
            out_bin = filename + ".out"
            subprocess.run(
                ["gcc", filename, "-o", out_bin],
                capture_output=True,
                text=True,
                timeout=10,
            )
            result = subprocess.run(
                [out_bin],
                input=input_str,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if os.path.exists(out_bin):
                os.remove(out_bin)

        return {"output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"output": "", "error": str(e)}
    finally:
        if os.path.exists(filename):
            os.remove(filename)




