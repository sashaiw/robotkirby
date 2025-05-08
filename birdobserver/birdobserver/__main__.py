from pathlib import Path

from birdnet import SpeciesPredictions, predict_species_within_audio_file



def predict():
    # predict species within the whole audio file
    audio_path = Path("soundscape.wav")
    predictions = SpeciesPredictions(predict_species_within_audio_file(audio_path))

    # get most probable prediction at time interval 0s-3s
    prediction, confidence = list(predictions[(0.0, 3.0)].items())[0]

    scientific_name, common_name = prediction.split("_")

    print(f"predicted '{prediction}' with a confidence of {confidence:.2f}")
    # output:
    # predicted 'Poecile atricapillus_Black-capped Chickadee' with a confidence of 0.81