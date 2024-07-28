using UnityEngine;

public class VideoDisplayManager : MonoBehaviour
{
    public VideoStreamReceiver streamReceiver;
    public Transform leftEyeQuad;
    public Transform rightEyeQuad;
    public float displayDistance = 2f;  // Increased distance
    public float displayWidth = 0.8f;   // Adjusted width
    public float displayHeight = 0.45f; // Adjusted height (16:9 aspect ratio)

    private Camera mainCamera;

    private void Start()
    {
        if (streamReceiver == null || leftEyeQuad == null || rightEyeQuad == null)
        {
            Debug.LogError("VideoDisplayManager: Missing references. Please check inspector.");
            return;
        }

        mainCamera = Camera.main;
        if (mainCamera == null)
        {
            Debug.LogError("Main Camera not found in the scene!");
            return;
        }

        SetupDisplays();
    }

    private void SetupDisplays()
    {
        SetupEyeDisplay(leftEyeQuad, -1);
        SetupEyeDisplay(rightEyeQuad, 1);

        // Set materials to use Unlit shader
        leftEyeQuad.GetComponent<Renderer>().material.shader = Shader.Find("Unlit/Texture");
        rightEyeQuad.GetComponent<Renderer>().material.shader = Shader.Find("Unlit/Texture");

        Debug.Log("Displays set up");
    }

    private void SetupEyeDisplay(Transform eyeQuad, int sideFactor)
    {
        eyeQuad.SetParent(mainCamera.transform, false);
        eyeQuad.localPosition = new Vector3(sideFactor * displayWidth / 4f, 0, displayDistance);
        eyeQuad.localRotation = Quaternion.identity;
        eyeQuad.localScale = new Vector3(displayWidth / 2f, displayHeight, 1f);
    }

    private void Update()
    {
        UpdateEyeTexture(leftEyeQuad.GetComponent<Renderer>(), streamReceiver.leftEyeTexture);
        UpdateEyeTexture(rightEyeQuad.GetComponent<Renderer>(), streamReceiver.rightEyeTexture);
    }

    private void UpdateEyeTexture(Renderer eyeRenderer, Texture texture)
    {
        if (texture != null && eyeRenderer.material.mainTexture != texture)
        {
            eyeRenderer.material.mainTexture = texture;
            Debug.Log($"Updated {eyeRenderer.name} texture");
        }
    }
}