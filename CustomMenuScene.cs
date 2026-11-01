using UnityEngine;

public enum ActionInterpType
{
    Linear,
    In,
    Out,
    InOut,
    MAX
};

public class AngleAction
{
    public float degrees;
    public ActionInterpType interpolation;
}

public class AnimAction
{
    public Sprite frame = null;
    public Vector2 scale = Vector2.one;
    public Vector2 offset;
    public Color color = Color.white;
    public AngleAction angle = new AngleAction();
    public ActionInterpType interpolation;
    public float delay;
}

public class CustomAnimation
{
    public Vector2 scale = Vector2.one;
    public Vector2 offset;
    public bool interpolate;
    public List<AnimAction> actions;
}

public class CustomScrollingBackgroundMod
{
    public string vanilla;
    public Sprite sprite;
};

public class CustomMenuScene
{
    public string name;
    public SceneConstants.MainMenuScenaryModeENUM ID;
    public Color backgroundColor;
    public AudioClip musicStart;
    public AudioClip musicLoop;
    public GameObject prefab;
    public CustomScrollingBackgroundMod scrollingBackground;
}