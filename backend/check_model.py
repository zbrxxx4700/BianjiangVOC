"""检查训练模型 vs 预训练底模"""
import os, sys, warnings
warnings.filterwarnings('ignore')
import torch

RVC_ROOT = r"D:\Software\RVC20240604-AMD"
os.chdir(RVC_ROOT)
sys.path.insert(0, RVC_ROOT)

# 加载底模
base_path = os.path.join(RVC_ROOT, "assets", "pretrained_v2", "f0G40k.pth")
base = torch.load(base_path, map_location='cpu')
base_model = base.get('model', {})  # 底模的 key 是 'model'

print(f"底模: {os.path.getsize(base_path)/1024/1024:.0f} MB")
print(f"底模 model keys: {list(base_model.keys())[:5]}")
print(f"底模参数数: {len(base_model)}")

# 加载训练模型
model_path = os.path.join(RVC_ROOT, "assets", "weights", "BianjiangRVC_V2_e23_s1288.pth")
cpt = torch.load(model_path, map_location='cpu')
w = cpt['weight']
print(f"\n训练模型: 参数数 {len(w)}, 共计 {sum(p.numel() for p in w.values())/1e6:.1f}M")

# 对比
common = set(w.keys()) & set(base_model.keys())
print(f"\n共同参数: {len(common)} / {len(w)}")

if len(common) > 0:
    # 平均绝对差异
    diffs = []
    for k in list(common)[:20]:  # 只看前20层
        d = (w[k] - base_model[k]).abs().mean().item()
        diffs.append(d)
        m = w[k].abs().mean().item()
        print(f"  {k}: 差异={d:.6f}, 幅度={m:.4f}")
    
    avg_diff = sum(diffs) / len(diffs)
    print(f"\n前20层平均差异: {avg_diff:.6f}")
    
    # emb_g 差异
    if 'emb_g.weight' in common:
        ed = (w['emb_g.weight'] - base_model['emb_g.weight']).abs().mean().item()
        print(f"emb_g.weight 差异: {ed:.6f}")
    
    if avg_diff < 0.01:
        print("\n!!! 模型与底模几乎没有差异，训练可能没生效 !!!")
    else:
        print("\n模型与底模有明显差异，训练有效")

# 不同 epoch 差异
print("\nEpoch 间差异对比:")
for ep in ["e10_s560", "e18_s1008", "e22_s1232"]:
    fp = os.path.join(RVC_ROOT, "assets", "weights", f"BianjiangRVC_V2_{ep}.pth")
    if os.path.exists(fp):
        c = torch.load(fp, map_location='cpu')['weight']
        d = sum((c[k] - w[k]).abs().mean().item() for k in c.keys() & w.keys()) / len(common)
        print(f"  {ep} vs e23: {d:.6f}")
