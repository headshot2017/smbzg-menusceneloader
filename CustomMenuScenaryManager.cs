using System.Collections;
using System.Reflection;
using UnityEngine;
using UnityEngine.UI;

public class CustomMenuScenaryManager : MonoBehaviour
{
    public MainMenuScenaryManager Comp_Manager;
    Coroutine Update_work;

    public bool isInit
    {
        get
        {
            return (bool)typeof(MainMenuScenaryManager).GetField("isInit", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(Comp_Manager);
        }
        set
        {
            typeof(MainMenuScenaryManager).GetField("isInit", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(Comp_Manager, value);
        }
    }
    public GameObject CurrentScenary
    {
        get
        {
            return (GameObject)typeof(MainMenuScenaryManager).GetField("CurrentScenary", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(Comp_Manager);
        }
        set
        {
            typeof(MainMenuScenaryManager).GetField("CurrentScenary", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(Comp_Manager, value);
        }
    }
    public Image ScenaryModeTransitionFade => Comp_Manager.ScenaryModeTransitionFade;

    public void Awake()
    {
        Comp_Manager = GetComponent<MainMenuScenaryManager>();
        Update_work = null;
    }

    public void Start()
    {
        Comp_Manager.Button_ToggleScenaryMode.onClick.RemoveAllListeners();
        Comp_Manager.Button_ToggleScenaryMode.onClick.AddListener(ToggleScenaryMode);
    }

    public void UpdateMainMenuScenaryByMode()
    {
        if (Update_work != null) return;
        Update_work = StartCoroutine(UpdateMainMenuScenaryByMode_Work());
    }

    IEnumerator UpdateMainMenuScenaryByMode_Work()
    {
        if (isInit)
        {
            ScenaryModeTransitionFade.gameObject.SetActive(value: true);
            ScenaryModeTransitionFade.SetAlpha(0f);
            float elapsed2 = 0f;
            for (float timeout2 = 1f; elapsed2 < timeout2; elapsed2 += Time.unscaledDeltaTime)
            {
                float newAlpha = elapsed2 / timeout2;
                ScenaryModeTransitionFade.SetAlpha(newAlpha);
                yield return null;
            }
        }

        CustomMenuScene aTheme = null;
        SceneConstants.MainMenuScenaryModeENUM currentMode = SaveData.Data.Get_MainMenuScenaryMode();
        Destroy(CurrentScenary);
        switch (currentMode)
        {
            case SceneConstants.MainMenuScenaryModeENUM.Halloween2022:
                Comp_Manager.TheCam.backgroundColor = Comp_Manager.BackgroundColor_Halloween;
                CurrentScenary = Instantiate(Comp_Manager.Scenary_Halloween_2022, ScenaryModeTransitionFade.transform.parent, worldPositionStays: false);
                break;
            case SceneConstants.MainMenuScenaryModeENUM.AprilFools2022:
                Comp_Manager.TheCam.backgroundColor = Comp_Manager.BackgroundColor_Classic;
                CurrentScenary = Instantiate(Comp_Manager.Scenary_April2022_Goomba, ScenaryModeTransitionFade.transform.parent, worldPositionStays: false);
                break;
            case SceneConstants.MainMenuScenaryModeENUM.YoshiIsland:
                Comp_Manager.TheCam.backgroundColor = Comp_Manager.BackgroundColor_YoshiIsland;
                CurrentScenary = Instantiate(Comp_Manager.Scenary_YoshisIsland, ScenaryModeTransitionFade.transform.parent, worldPositionStays: false);
                break;
            case SceneConstants.MainMenuScenaryModeENUM.RebootEnding:
                Comp_Manager.TheCam.backgroundColor = Comp_Manager.BackgroundColor_Classic;
                CurrentScenary = Instantiate(Comp_Manager.Scenary_RebootEnding, ScenaryModeTransitionFade.transform.parent, worldPositionStays: false);
                break;
            case SceneConstants.MainMenuScenaryModeENUM.SemiSuperA:
                Comp_Manager.TheCam.backgroundColor = Comp_Manager.BackgroundColor_SemiSuperA;
                CurrentScenary = Instantiate(Comp_Manager.Scenary_SemiSuperA, ScenaryModeTransitionFade.transform.parent, worldPositionStays: false);
                break;
            case SceneConstants.MainMenuScenaryModeENUM.RNGCheck:
                Comp_Manager.TheCam.backgroundColor = Comp_Manager.BackgroundColor_SemiSuperA;
                CurrentScenary = Instantiate(Comp_Manager.Scenary_GoombaNuke, ScenaryModeTransitionFade.transform.parent, worldPositionStays: false);
                break;
            case SceneConstants.MainMenuScenaryModeENUM.SemiSuperB:
                Comp_Manager.TheCam.backgroundColor = Comp_Manager.BackgroundColor_SemiSuperB;
                CurrentScenary = Instantiate(Comp_Manager.Scenary_SemiSuperB, ScenaryModeTransitionFade.transform.parent, worldPositionStays: false);
                break;
            case SceneConstants.MainMenuScenaryModeENUM.SemiSuperC:
                Comp_Manager.TheCam.backgroundColor = Comp_Manager.BackgroundColor_SemiSuperB;
                CurrentScenary = Instantiate(Comp_Manager.Scenary_SemiSuperC, ScenaryModeTransitionFade.transform.parent, worldPositionStays: false);
                break;
            default:
                aTheme = MenuSceneLoader.Core.MenuScenes.Find(theme => theme.ID == currentMode);
                if (aTheme != null)
                {
                    Comp_Manager.TheCam.backgroundColor = aTheme.backgroundColor;
                    CurrentScenary = Instantiate(aTheme.prefab, ScenaryModeTransitionFade.transform.parent, worldPositionStays: false);
                    CurrentScenary.gameObject.SetActive(true);

                    for (int i=0; i<aTheme.prefab.transform.childCount; i++)
                    {
                        CustomAnimator_Menu animatorPrefab = aTheme.prefab.transform.GetChild(i).GetComponent<CustomAnimator_Menu>();
                        CustomAnimator_Menu animatorClone = CurrentScenary.transform.GetChild(i).GetComponent<CustomAnimator_Menu>();

                        animatorClone.SetAnim(animatorPrefab.m_CurrentAnimation);
                        animatorClone.Play();
                    }
                    break;
                }

                Comp_Manager.TheCam.backgroundColor = Comp_Manager.BackgroundColor_Classic;
                CurrentScenary = Instantiate(Comp_Manager.Scenary_Classic, ScenaryModeTransitionFade.transform.parent, worldPositionStays: false);
                break;
        }

        CurrentScenary.transform.SetSiblingIndex(ScenaryModeTransitionFade.transform.GetSiblingIndex());
        if (isInit)
        {
            ScenaryModeTransitionFade.SetAlpha(1f);
            float timeout2 = 0f;
            for (float elapsed2 = 1f; timeout2 < elapsed2; timeout2 += Time.unscaledDeltaTime)
            {
                float num = timeout2 / elapsed2;
                ScenaryModeTransitionFade.SetAlpha(1f - num);
                yield return null;
            }

            ScenaryModeTransitionFade.gameObject.SetActive(value: false);
        }

        isInit = true;
        Update_work = null;
        if (currentMode != SaveData.Data.Get_MainMenuScenaryMode())
        {
            Update_work = StartCoroutine(UpdateMainMenuScenaryByMode_Work());
        }
    }

    private void ToggleScenaryMode()
    {
        SceneConstants.MainMenuScenaryModeENUM mainMenuScenaryModeENUM = SaveData.Data.Get_MainMenuScenaryMode();
        mainMenuScenaryModeENUM++;
        if (mainMenuScenaryModeENUM == SceneConstants.MainMenuScenaryModeENUM.RNGCheck && UnityEngine.Random.Range(0, 10) != 2)
            mainMenuScenaryModeENUM++;

        if (!MenuSceneLoader.Core.ContainsMenu(mainMenuScenaryModeENUM))
        {
            if (mainMenuScenaryModeENUM < (SceneConstants.MainMenuScenaryModeENUM)1000)
                mainMenuScenaryModeENUM = (SceneConstants.MainMenuScenaryModeENUM)1000; // enter custom menus
            else
                mainMenuScenaryModeENUM = SceneConstants.MainMenuScenaryModeENUM.Classic; // go back to vanilla
        }

        SaveData.Data.Set_MainMenuScenaryMode(mainMenuScenaryModeENUM);
        SaveData.Save();
    }
}