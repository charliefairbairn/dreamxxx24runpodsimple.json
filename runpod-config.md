# RunPod Serverless Endpoint Setup Guide

This repository contains a ComfyUI workflow configured for RunPod serverless endpoints.

## Repository Connection

The repository is connected to: `https://github.com/charliefairbairn/dreamxxx24runpodsimple.json.git`

## Files Included

- `Dockerfile` - Container configuration with ComfyUI and required models
- `handler.py` - RunPod serverless handler for processing workflows
- `requirements.txt` - Python dependencies
- `example-request.json` - Example workflow payload

## Deployment Steps

### 1. Connect GitHub to RunPod

1. Log in to your RunPod account
2. Navigate to **Settings** > **Connections**
3. Under GitHub section, click **Connect** and authorize RunPod

### 2. Create Serverless Endpoint

1. In RunPod console, go to **Serverless** section
2. Click **New Endpoint**
3. Choose **Import Git Repository**
4. Select `charliefairbairn/dreamxxx24runpodsimple.json`
5. Configure settings:
   - **Endpoint Name**: Your desired name
   - **Endpoint Type**: Queue or Load Balancer
   - **GPU Configuration**: Select appropriate GPU (recommended: RTX 3090 or better)
   - **Container Start Command**: `python /handler.py`
   - **Exposed Port**: `8188` (ComfyUI default)
6. Click **Create Endpoint**

### 3. Test the Endpoint

Once deployed, use the endpoint API URL to send requests:

```bash
curl -X POST https://api.runpod.ai/v2/{endpoint_id}/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d @example-request.json
```

## Workflow Structure

The handler expects input in one of these formats:

```json
{
  "input": {
    "workflow": {
      // ComfyUI workflow nodes
    }
  }
}
```

Or:

```json
{
  "workflow": {
    // ComfyUI workflow nodes
  }
}
```

## Response Format

```json
{
  "prompt_id": "prompt_id_string",
  "filename": "generated_image.png",
  "image": "base64_encoded_image",
  "status": "completed"
}
```

