using HarmonyLib;
using MelonLoader;
using System.Reflection;
using UnityEngine;

[assembly: MelonInfo(typeof(MenuSceneLoader.Core), "MenuSceneLoader", "1.0.0", "Headshotnoby/Headshot2017", null)]
[assembly: MelonGame("Jonathan Miller aka Zethros", "SMBZ-G")]

namespace MenuSceneLoader
{
    public class Core : MelonMod
    {
        public static List<CustomMenuScene> MenuScenes = new List<CustomMenuScene>();
        public static bool IsLoading;

        public override void OnInitializeMelon()
        {
            LoggerInstance.Msg("Initialized.");
            IsLoading = true;
        }

        public override void OnLateInitializeMelon()
        {
            GameObject obj = new GameObject("MenuSceneLoader", typeof(SceneryLoaderComponent));
            GameObject.DontDestroyOnLoad(obj);
        }


        public static bool ContainsMenu(SceneConstants.MainMenuScenaryModeENUM id)
        {
            return Enum.IsDefined(typeof(SceneConstants.MainMenuScenaryModeENUM), id) || MenuScenes.Any( theme => theme.ID == id );
        }

        [HarmonyPatch(typeof(SaveData.GameSaveData_Type), "Get_MainMenuScenaryMode")]
        private static class GetMainMenuScenaryPatch
        {
            private static bool Prefix(ref SceneConstants.MainMenuScenaryModeENUM __result)
            {
                SceneConstants.MainMenuScenaryModeENUM MainMenuScenaryMode = (SceneConstants.MainMenuScenaryModeENUM)typeof(SaveData.GameSaveData_Type).GetField("MainMenuScenaryMode", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(SaveData.Data);
                CustomMenuScene theme = MenuScenes.Find((theme) => theme.ID == MainMenuScenaryMode);
                if (theme != null)
                {
                    __result = theme.ID;
                    return false;
                }
                return true;
            }
        }

        [HarmonyPatch(typeof(MainMenuScenaryManager), "UpdateMainMenuScenaryByMode")]
        private static class UpdateMenuScenaryPatch
        {
            private static bool Prefix(MainMenuScenaryManager __instance)
            {
                GameObject obj = GameObject.Find("MainMenuScript");
                CustomMenuScenaryManager comp = obj.GetComponent<CustomMenuScenaryManager>();
                if (!comp) comp = obj.AddComponent<CustomMenuScenaryManager>();
                comp.UpdateMainMenuScenaryByMode();
                return false;
            }
        }

        [HarmonyPatch(typeof(AutoBGMPlayer), "UpdateMenuMusicByMode")]
        private static class UpdateMenuMusicPatch
        {
            private static bool Prefix(AutoBGMPlayer __instance)
            {
                CustomMenuScene theme = MenuScenes.Find((theme) => theme.ID == SaveData.Data.Get_MainMenuScenaryMode());
                if (theme == null) return true;

                bool flag = PersistantBGM.ins.CurrentAudioSource == null || (PersistantBGM.ins.CurrentAudioSource.clip != theme.musicStart && PersistantBGM.ins.CurrentAudioSource.clip != theme.musicLoop);
                if (flag)
                {
                    if (theme.musicStart != theme.musicLoop && theme.musicStart != null)
                    {
                        PersistantBGM.ins.ClearPlaylist();
                        PersistantBGM.ins.PlayNewMusic(theme.musicStart, loop: false);
                        PersistantBGM.ins.AddMusicToQueue(theme.musicLoop, loop: true);
                    }
                    else if (theme.musicLoop != null)
                        PersistantBGM.ins.PlayNewMusic(theme.musicLoop, loop: true);
                }

                typeof(AutoBGMPlayer).GetField("isInit", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(__instance, true);
                return false;
            }
        }

        [HarmonyPatch(typeof(IntroScript), "Update")]
        private static class IntroClassPatch
        {
            private static bool Prefix(IntroScript __instance)
            {
                FieldInfo fCountdown = typeof(IntroScript).GetField("countdown", BindingFlags.Instance | BindingFlags.NonPublic);
                float countdown = (float)fCountdown.GetValue(__instance);
                if (!(countdown > 0f))
                {
                    return false;
                }

                countdown -= Time.unscaledDeltaTime;
                if (!(countdown <= 0f))
                {
                    return false;
                }

                if (CharacterSkinManager.ins.IsLoading || IsLoading)
                {
                    fCountdown.SetValue(__instance, 0.25f);
                    return false;
                }

                if (!GC.ins.enabled)
                {
                    Debug.Log("GC instance is diabled. Enabling...");
                    GC.ins.enabled = true;
                }

                Debug.Log("Loading Main Menu...");
                GC.ins.LoadScene("MainMenu");

                return false;
            }
        }
    }
}