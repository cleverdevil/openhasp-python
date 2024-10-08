import openhasp as hasp
# from plates import retroshow as _  # noqa
from plates import frontroom as _  # noqa
from plates import office as _  # noqa
from plates import theater as _  # noqa

print("Generating plate jsonl for all plates ...")
for name, jsonl in hasp.plates.jsonl.items():
    with open(f"output/plate-{name}.jsonl", "w") as f:
        f.write(jsonl)

print("Generating 'openhasp.yaml' ...")
with open("output/openhasp.yaml", "w") as f:
    f.write(hasp.plates.hass_yaml)

print("Generating 'openhasp_automations.yaml' ...")
with open("output/openhasp_automations.yaml", "w") as f:
    f.write(hasp.plates.hass_automations_yaml)

print("Done!")
