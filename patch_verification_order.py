path = "games/louvo/run.py"
with open(path, "r") as f:
    content = f.read()

old_line = '    if run_conditions["run_format_checks"] and not failed_modes:'

new_block = '''    if run_conditions["run_format_checks"] and not failed_modes:
        import glob
        for verification_file in glob.glob(
            os.path.join(config.library_path, "configs", "*.verification.json")
        ):
            os.remove(verification_file)'''

if old_line not in content:
    print("ERREUR : ligne non trouvee telle quelle, rien modifie.")
elif "for verification_file in glob.glob" in content:
    print("Deja applique, rien a faire.")
else:
    content = content.replace(old_line, new_block, 1)
    with open(path, "w") as f:
        f.write(content)
    print("OK : suppression des sidecars deplacee juste avant les tests de format.")
