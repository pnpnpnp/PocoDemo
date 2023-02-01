要修改的地方：
heroActivityTest.py的activityDict
config.ini
auto_setup窗口句柄（getUnityWindowHandle.py可以拿到窗口句柄）

poco-sdk相关：
https://www.cnblogs.com/lucio1128/p/12975449.html
Newtonsoft.Json位置E:\20210820_eu\client\main\Assets\Editor\MemoryProfiler\JsonDotNet20
Newtonsoft.Json.dll和Newtonsoft.Json.dll.meta两个文件
x4用的是ugui
----------------------------------------------------------------------------------------------------
进度：
activityDict优化
configTable
translateTable
打印测试结果描述加上具体什么地方错了

相关优化问题：
比较大型的游戏，局内战斗的元素和UI的复杂程度也是很高的，
保存一次UI树的信息也有2M以上的数据，而获取时间会随着UI复杂度的上升而上升。
从最终效果来看，获取时间会由1秒到4秒逐渐上升，这样的速度是不能满足实现业务需求的，
因此建议从poco的unitySDK上添加黑名单机制，以提高获取UITree的效率。

黑名单过滤掉Node不需要的属性减少dump出来的json文件大小：
修改UnityNode.cs的enumerateAttrs接口
        public override Dictionary<string, object> enumerateAttrs()
        {
            Dictionary<string, object> payload = GetPayload();
            Dictionary<string, object> ret = new Dictionary<string, object>();
            string blackList = "clickable|text|components|texture|tag|_ilayer|layer|_instanceId";
            foreach (KeyValuePair<string, object> p in payload)
            {
                if (blackList.Contains(p.Key))
                {
                    continue;
/*                     ret.Add(p.Key, p.Value); */
                }
                ret.Add(p.Key,p.Value);
            }
            return ret;
        }

黑名单过滤掉不需要的Node减少dump出来的json文件大小：
修改AbstractDumper.cs的dumpHierarchyImpl接口（注释部分）
        private Dictionary<string, object> dumpHierarchyImpl(AbstractNode node, bool onlyVisibleNode)
        {
            if (node == null)
            {
                return null;
            }
            Dictionary<string, object> payload = node.enumerateAttrs();
            Dictionary<string, object> result = new Dictionary<string, object>();
            string name = (string)node.getAttr("name");
            result.Add("name", name);
            result.Add("payload", payload);

            List<object> children = new List<object>();
            foreach (AbstractNode child in node.getChildren())
            {
/* 				string needName = (string)child.getAttr("name");
				string needLayer = (string)child.getAttr("layer");
				if (needName != "UI" && needLayer != "UI")
				{
					continue;
				} */
                if (!onlyVisibleNode || (bool)child.getAttr("visible"))
                {
                    children.Add(dumpHierarchyImpl(child, onlyVisibleNode));
                }
            }
            if (children.Count > 0)
            {
                result.Add("children", children);
            }
            return result;
        }

利用freeze函数： 多次提取会重复的获取UI元素浪费时间，
freeze() --获取当前UI树的一个静态副本
不过这种方法也是有局限性的，如果是频繁切换界面，
并且在当前界面的操作很少的话，不推荐使用

minicap截图：截图服务启动会消耗时间且截图本身也消耗性能
airtest\core\settings.py
ST.SAVE_IMAGE = False