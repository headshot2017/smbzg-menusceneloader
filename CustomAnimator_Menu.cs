using UnityEngine;


public class InterpHelper
{
    public static float Linear(float x)
    {
        return x;
    }

    public static float In(float x)
    {
        return x * x;
    }

    public static float Out(float x)
    {
        return 1 - (1 - x) * (1 - x);
    }

    public static float InOut(float x)
    {
        return x < 0.5f ? 2 * x * x : 1 - Mathf.Pow(-2 * x + 2, 2) / 2;
    }

    public static Dictionary<ActionInterpType, Func<float, float>> Dict = new Dictionary<ActionInterpType, Func<float, float>>
    {
        {ActionInterpType.Linear, Linear},
        {ActionInterpType.In, In},
        {ActionInterpType.Out, Out},
        {ActionInterpType.InOut, InOut},
    };
};

public class CustomAnimator_Menu : MonoBehaviour
{
    public CustomAnimation m_CurrentAnimation = null;
    UnityEngine.UI.Image m_CompImage;

    bool m_Playing;
    float m_Time;
    public int m_Frame { get; private set; }

    public void Awake()
    {
        m_CompImage = GetComponent<UnityEngine.UI.Image>();
        m_Playing = false;
        m_Time = 0;
        m_Frame = 0;
    }

    public void Update()
    {
        if (!m_Playing || m_CurrentAnimation.actions.Count <= 0) return;

        InterpolateFrames();

        AnimAction currAction = m_CurrentAnimation.actions[m_Frame];

        while ((m_Time += Time.deltaTime) > currAction.delay)
        {
            if (currAction.delay <= 0)
                m_Time = currAction.delay - Time.deltaTime;
            else
                m_Time -= currAction.delay;

            m_Frame = (m_Frame + 1) % m_CurrentAnimation.actions.Count;

            currAction = m_CurrentAnimation.actions[m_Frame];

            if (OnFrameChange()) return;
        }
    }

    bool OnFrameChange()
    {
        if (m_CurrentAnimation.actions.Count <= 0)
            return true;

        AnimAction currAction = m_CurrentAnimation.actions[m_Frame];

        SetColor(currAction.color);
        SetScale();
        SetOffset();
        SetAngle();
        if (currAction.frame != null)
            SetSprite(currAction.frame);

        return false;
    }

    public void SetAnim(CustomAnimation animation)
    {
        m_CurrentAnimation = animation;

        m_Time = 0;
        m_Frame = 0;
        m_Playing = false;
        OnFrameChange();
    }

    public void SetSprite(Sprite spr)
    {
        m_CompImage.sprite = spr;
    }

    public void SetColor(Color color)
    {
        m_CompImage.color = color;
    }

    public void SetScale()
    {
        AnimAction currAction = m_CurrentAnimation.actions[m_Frame];

        m_CompImage.transform.localScale = new Vector3(
            m_CurrentAnimation.scale.x * currAction.scale.x,
            m_CurrentAnimation.scale.y * currAction.scale.y,
        1);
    }

    public void SetOffset()
    {
        AnimAction currAction = m_CurrentAnimation.actions[m_Frame];
        m_CompImage.transform.localPosition = m_CurrentAnimation.offset + currAction.offset;
    }

    public void SetAngle()
    {
        AnimAction currAction = m_CurrentAnimation.actions[m_Frame];
        m_CompImage.transform.localEulerAngles = new Vector3(0, 0, -currAction.angle.degrees);
    }

    public void Stop()
    {
        if (!m_Playing) return;
        m_Playing = false;
    }

    public bool Play(bool replay = false)
    {
        if (m_Playing && !replay)
            return true;

        m_Time = 0;
        m_Frame = 0;
        m_Playing = true;
        OnFrameChange();
        return true;
    }

    void InterpolateFrames()
    {
        if (m_CurrentAnimation == null || !m_CurrentAnimation.interpolate) return;

        AnimAction currAction = m_CurrentAnimation.actions[m_Frame];
        if (currAction.delay <= 0) return;

        float lerp = m_Time / currAction.delay;
        float xAngle = m_Time / currAction.delay;
        if (currAction.interpolation >= 0 && currAction.interpolation <= ActionInterpType.MAX)
        {
            lerp = InterpHelper.Dict[currAction.interpolation](lerp);
        }

        AnimAction nextAction;
        if (m_Frame >= m_CurrentAnimation.actions.Count - 1)
            nextAction = m_CurrentAnimation.actions[0];
        else
            nextAction = m_CurrentAnimation.actions[m_Frame + 1];

        Color colorLerp = Color.Lerp(currAction.color, nextAction.color, lerp);

        Vector2 scaleLerp = m_CurrentAnimation.scale;
        scaleLerp.x *= Mathf.Lerp(currAction.scale.x, nextAction.scale.x, lerp);
        scaleLerp.y *= Mathf.Lerp(currAction.scale.y, nextAction.scale.y, lerp);

        Vector2 offsetLerp = m_CurrentAnimation.offset;
        offsetLerp.x += Mathf.Lerp(currAction.offset.x, nextAction.offset.x, lerp);
        offsetLerp.y += Mathf.Lerp(currAction.offset.y, nextAction.offset.y, lerp);

        float angleLerp = Mathf.Lerp(
            currAction.angle.degrees,
            nextAction.angle.degrees,
            InterpHelper.Dict[currAction.angle.interpolation](xAngle)
        );


        m_CompImage.transform.localPosition = offsetLerp;
        m_CompImage.transform.localEulerAngles = new Vector3(0, 0, -angleLerp);
        m_CompImage.transform.localScale = scaleLerp;
        m_CompImage.color = colorLerp;
    }
}