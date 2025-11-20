import runpod
import requests
import json
import time
import os
import base64

# ComfyUI API endpoint (default port for RunPod ComfyUI workers)
COMFYUI_URL = os.getenv("COMFYUI_URL", "http://127.0.0.1:8188")

def wait_for_comfyui(max_wait=300):
    """Wait for ComfyUI to be ready"""
    for i in range(max_wait):
        try:
            response = requests.get(f"{COMFYUI_URL}/system_stats", timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def get_workflow_from_input(job_input):
    """Extract workflow from job input"""
    if isinstance(job_input, dict):
        if "workflow" in job_input:
            return job_input["workflow"]
        elif "input" in job_input and "workflow" in job_input["input"]:
            return job_input["input"]["workflow"]
    return job_input

def queue_prompt(workflow):
    """Queue a prompt to ComfyUI"""
    p = {"prompt": workflow}
    data = json.dumps(p).encode('utf-8')
    
    response = requests.post(f"{COMFYUI_URL}/prompt", data=data)
    return response.json()

def get_image(prompt_id):
    """Get the generated image from ComfyUI"""
    max_attempts = 100
    for attempt in range(max_attempts):
        response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}")
        history = response.json()
        
        if prompt_id in history:
            for node_id in history[prompt_id]["outputs"]:
                node_output = history[prompt_id]["outputs"][node_id]
                if "images" in node_output:
                    for image in node_output["images"]:
                        image_data = requests.get(f"{COMFYUI_URL}/view?filename={image['filename']}&subfolder={image.get('subfolder', '')}&type={image.get('type', 'output')}")
                        return image_data.content, image['filename']
        
        time.sleep(1)
    
    raise Exception("Timeout waiting for image generation")

def handler(job):
    """RunPod serverless handler"""
    try:
        # Wait for ComfyUI to be ready
        if not wait_for_comfyui():
            return {
                "error": "ComfyUI service is not ready. Please wait and try again."
            }
        
        job_input = job.get("input", {})
        
        # Extract workflow from input
        workflow = get_workflow_from_input(job_input)
        
        if not workflow:
            return {
                "error": "No workflow found in input. Please provide a workflow in the 'workflow' field or 'input.workflow' field."
            }
        
        # Queue the prompt
        result = queue_prompt(workflow)
        
        if "error" in result:
            return {"error": result["error"]}
        
        prompt_id = result["prompt_id"]
        
        # Wait for and get the image
        image_data, filename = get_image(prompt_id)
        
        # Convert image to base64 for return
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        return {
            "prompt_id": prompt_id,
            "filename": filename,
            "image": image_base64,
            "status": "completed"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "traceback": str(e.__class__.__name__)
        }

runpod.serverless.start({"handler": handler})

