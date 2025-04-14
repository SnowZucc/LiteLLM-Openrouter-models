import requests
import json
import os
from litellm import model_cost
import traceback

def fetch_openrouter_models():
    try:
        url = "https://openrouter.ai/api/v1/models"
        response = requests.get(url)
        response.raise_for_status()  # Vérifie si la requête a réussi
        return response.json()
    except Exception as e:
        print(f"Erreur lors de la récupération des modèles OpenRouter: {e}")
        traceback.print_exc()
        return {"data": []}

def fetch_litellm_models():
    try:
        url = "https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json"
        response = requests.get(url)
        response.raise_for_status()  # Vérifie si la requête a réussi
        return response.json()
    except Exception as e:
        print(f"Erreur lors de la récupération des modèles LiteLLM: {e}")
        traceback.print_exc()
        return {}

def openrouter_model_to_litellm(model):
    return { 
        "max_tokens": model['context_length'],
        "input_cost_per_token": float(model['pricing']['prompt']),
        "output_cost_per_token": float(model['pricing']['completion']),
        "litellm_provider": "openrouter",
        "mode": "chat"
    }  

try:
    # Récupérer les modèles depuis OpenRouter
    print("Récupération des modèles OpenRouter...")
    or_response = fetch_openrouter_models()
    openrouter_models = or_response.get('data', [])
    print(f"Nombre de modèles OpenRouter récupérés: {len(openrouter_models)}")
    
    # Télécharger le fichier de modèles LiteLLM existant
    print("Téléchargement des modèles LiteLLM...")
    litellm_models = fetch_litellm_models()
    print(f"Nombre de modèles LiteLLM récupérés: {len(litellm_models)}")
    
    # Mettre à jour model_cost de litellm
    print("Mise à jour des modèles...")
    for model in openrouter_models:
        model_id = f'openrouter/{model["id"]}'
        model_data = openrouter_model_to_litellm(model)
        model_cost[model_id] = model_data
        
        # Ajouter au dictionnaire des modèles LiteLLM
        litellm_models[model_id] = model_data
    
    # Vérifier le répertoire de travail actuel
    print(f"Répertoire de travail actuel: {os.getcwd()}")
    
    # Exporter le fichier combiné en JSON
    output_path = 'combined_models.json'
    print(f"Tentative d'écriture du fichier {output_path}...")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(litellm_models, f, indent=4)
    
    print(f"Fichier {output_path} écrit avec succès")
    print(f"Taille du fichier: {os.path.getsize(output_path)} octets")
    
    # Également exporter uniquement les modèles OpenRouter pour référence
    export_models = {}
    for model in openrouter_models:
        export_models[f'openrouter/{model["id"]}'] = openrouter_model_to_litellm(model)

    export_path = 'openrouter_models.json'
    print(f"Tentative d'écriture du fichier {export_path}...")
    
    with open(export_path, 'w', encoding='utf-8') as f:
        json.dump(export_models, f, indent=2)
    
    print(f"Fichier {export_path} écrit avec succès")
    print(f"Taille du fichier: {os.path.getsize(export_path)} octets")

    print(f"Les modèles OpenRouter ont été ajoutés aux modèles LiteLLM dans '{output_path}'")
    print(f"Les modèles OpenRouter ont également été exportés séparément dans '{export_path}'")

except Exception as e:
    print(f"Une erreur s'est produite: {e}")
    traceback.print_exc()