using MelonLoader;
using MyBox;
using System;
using System.Collections;
using System.Reflection;
using TinyJSON;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;

public class SceneryLoaderComponent : MonoBehaviour
{
    public Texture2D texture;

    void Start()
    {
        StartCoroutine(LoadMenuScenes());
    }

    IEnumerator LoadMenuScenes()
    {
        MenuSceneLoader.Core.MenuScenes.Clear();

        if (!Directory.Exists($"{Application.streamingAssetsPath}/MenuScenes"))
            Directory.CreateDirectory($"{Application.streamingAssetsPath}/MenuScenes");

        foreach (String _dirName in Directory.EnumerateDirectories($"{Application.streamingAssetsPath}/MenuScenes"))
        {
            string path = _dirName.Replace('\\', '/');
            string dirName = Path.GetFileName(path);

            ProxyObject json = JSON.Load(File.ReadAllText($"{path}/menu.json")) as ProxyObject;
            int version = json.Keys.Contains("version") ? json["version"] : 1;

            Melon<MenuSceneLoader.Core>.Logger.Msg($"MenuSceneLoader: Loading '{dirName}', version {version}");
            Debug.Log($"MenuSceneLoader: Loading '{dirName}', version {version}");

            CustomMenuScene theme = new() {
                ID = (SceneConstants.MainMenuScenaryModeENUM)(MenuSceneLoader.Core.MenuScenes.Count + 1000),
                prefab = new GameObject($"Scenery: {dirName}"),
                backgroundColor = json.Keys.Contains("backgroundColor") ? new Color(json["backgroundColor"][0] / 255f, json["backgroundColor"][1] / 255f, json["backgroundColor"][2] / 255f) : Color.white
            };
            DontDestroyOnLoad(theme.prefab);
            RectTransform t = theme.prefab.AddComponent<RectTransform>();
            t.anchoredPosition = new Vector2(0, 720/2);
            t.anchorMax = new Vector2(0.5f, 0);
            t.anchorMin = new Vector2(0.5f, 0);
            t.offsetMax = new Vector2(0.5f, 720/2-0.5f);
            t.offsetMin = new Vector2(-0.5f, 720/2-0.5f);
            t.sizeDelta = Vector2.one;

            UnityWebRequest www;
            if (File.Exists($"{path}/loop.ogg"))
            {
                www = UnityWebRequestMultimedia.GetAudioClip($"file:///{path}/loop.ogg", AudioType.OGGVORBIS);
                www.SendWebRequest();
                while (!www.isDone) ;

                theme.musicLoop = DownloadHandlerAudioClip.GetContent(www);

                if (File.Exists($"{path}/start.ogg"))
                {
                    www = UnityWebRequestMultimedia.GetAudioClip($"file:///{path}/start.ogg", AudioType.OGGVORBIS);
                    www.SendWebRequest();
                    while (!www.isDone) ;

                    theme.musicStart = DownloadHandlerAudioClip.GetContent(www);
                }
                else
                    theme.musicStart = theme.musicLoop;
            }
            else if (json.Keys.Contains("vanillaMusic"))
            {
                FieldInfo field = typeof(SoundCache).GetField($"BGM_{json["vanillaMusic"]}", BindingFlags.Instance | BindingFlags.Public);
                if (field != null)
                    theme.musicStart = theme.musicLoop = (AudioClip)field.GetValue(SoundCache.ins);
                else
                    Melon<MenuSceneLoader.Core>.Logger.Msg($"WARNING: {dirName}: Vanilla music '{json["vanillaMusic"]}' not found");
            }

            if (json.Keys.Contains("objects"))
            {
                ProxyArray arr = json["objects"] as ProxyArray;
                foreach (ProxyObject obj in arr)
                {
                    GameObject GameObj = new GameObject(obj["name"]);
                    Image Comp_Image = GameObj.AddComponent<Image>();
                    CustomAnimator_Menu Comp_CustomAnimator = GameObj.AddComponent<CustomAnimator_Menu>();

                    GameObj.transform.SetParent(theme.prefab.transform, false);

                    yield return TextureDownload(Uri.EscapeUriString($"file:///{path}/sprites/{obj["sprite"]}.png"));
                    if (!obj.Keys.Contains("filter") || !obj["filter"]) texture.filterMode = FilterMode.Point;
                    Comp_Image.rectTransform.sizeDelta = new Vector2(texture.width, texture.height);
                    Comp_Image.preserveAspect = true;

                    CustomAnimation anim = new();

                    if (obj.Keys.Contains("offset"))
                        anim.offset = new Vector2(obj["offset"][0], obj["offset"][1]);
                    if (obj.Keys.Contains("scale"))
                        anim.scale = new Vector2(obj["scale"][0], obj["scale"][1]);
                    anim.interpolate = (!obj.Keys.Contains("interpolate") || obj["interpolate"]);

                    if (obj.Keys.Contains("frames"))
                    {
                        anim.actions = new();
                        ProxyArray framesArray = obj["frames"] as ProxyArray;
                        foreach (ProxyObject actionVar in framesArray)
                        {
                            AnimAction action = new AnimAction();

                            if (actionVar.Keys.Contains("frame"))
                            {
                                Variant frameVar = actionVar["frame"];
                                int x = frameVar[0];
                                int y = frameVar[1];
                                int w = frameVar[2];
                                int h = frameVar[3];
                                if (w < 0) w = texture.width - x;
                                if (h < 0) h = texture.height - y;

                                if (w == 0)
                                {
                                    Melon<MenuSceneLoader.Core>.Logger.Msg($"WARNING: {dirName}: {obj["name"]} has a 'frame' action with width = zero! ({x}, {y}, {w}, {h})");
                                    w = texture.width;
                                }
                                if (h == 0)
                                {
                                    // don't divide by zero, warn the user too
                                    Melon<MenuSceneLoader.Core>.Logger.Msg($"WARNING: {dirName}: {obj["name"]} has a 'frame' action with height = zero! ({x}, {y}, {w}, {h})");
                                    h = texture.height;
                                }

                                action.frame = Sprite.Create(texture, new Rect(x, texture.height - y - h, w, h), new Vector2(0, 0));
                            }

                            if (actionVar.Keys.Contains("scale"))
                                action.scale = new Vector2(actionVar["scale"][0], actionVar["scale"][1]);

                            if (actionVar.Keys.Contains("offset"))
                                action.offset = new Vector2(actionVar["offset"][0], actionVar["offset"][1]);

                            if (actionVar.Keys.Contains("angle"))
                            {
                                Variant angle = actionVar["angle"];
                                if (angle as ProxyObject != null)
                                {
                                    action.angle.degrees = angle["degrees"];
                                    action.angle.interpolation = (ActionInterpType)((int)angle["interpolation"]);
                                }
                                else
                                    action.angle.degrees = angle;
                            }

                            if (actionVar.Keys.Contains("color"))
                                action.color = new Color(
                                    actionVar["color"][0] / 255f,
                                    actionVar["color"][1] / 255f,
                                    actionVar["color"][2] / 255f,
                                    actionVar["color"][3] / 255f
                                );

                            if (actionVar.Keys.Contains("interpolation"))
                                action.interpolation = (ActionInterpType)((int)actionVar["interpolation"]);

                            action.delay = (actionVar.Keys.Contains("delay")) ? (float)actionVar["delay"] : 0;

                            anim.actions.Add(action);
                        }
                    }

                    Comp_CustomAnimator.SetAnim(anim);
                }
            }

            theme.prefab.SetActive(false);

            MenuSceneLoader.Core.MenuScenes.Add(theme);
        }

        Melon<MenuSceneLoader.Core>.Logger.Msg("MenuSceneLoader: Loading complete");
        Debug.Log("MenuSceneLoader: Loading complete");
        MenuSceneLoader.Core.IsLoading = false;
        Destroy(gameObject);
        yield return null;
    }

    IEnumerator TextureDownload(string url)
    {
        using (UnityWebRequest www = UnityWebRequestTexture.GetTexture(url))
        {
            yield return www.SendWebRequest();
            texture = DownloadHandlerTexture.GetContent(www);
        }
    }
}