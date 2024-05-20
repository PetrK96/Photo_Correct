import PIL.Image
from carvekit.api.interface import Interface
from carvekit.ml.wrap.fba_matting import FBAMatting
from carvekit.ml.wrap.scene_classifier import SceneClassifier
from carvekit.ml.wrap.cascadepsp import CascadePSP
from carvekit.ml.wrap.tracer_b7 import TracerUniversalB7
from carvekit.pipelines.postprocessing import CasMattingMethod
from carvekit.pipelines.preprocessing import AutoScene
from carvekit.trimap.generator import TrimapGenerator

# Используем GPU для максимального качества обработки
device = 'cuda'

# Объявляем компоненты с использованием GPU и максимальных настроек качества
seg_net = TracerUniversalB7(device=device, batch_size=1, fp16=False)

cascade_psp = CascadePSP(
    device=device,
    batch_size=1,
    input_tensor_size=2048,  # Увеличенный размер тензора для лучшего качества
    fp16=False,
    processing_accelerate_image_size=4096,  # Увеличенный размер для ускоренной обработки
    global_step_only=False  # Используем все шаги для максимальной точности
)

fba = FBAMatting(
    device=device,
    input_tensor_size=4096,  # Максимальный размер тензора для наилучшего качества
    batch_size=1,
    fp16=False
)

trimap = TrimapGenerator(
    filter_threshold=-1,
    prob_threshold=255,  # Максимальный порог вероятности для минимального шума
    kernel_size=50,  # Увеличенный размер ядра для более точной маски
    erosion_iters=10  # Увеличенное количество итераций эрозии для более детальной маски
)

scene_classifier = SceneClassifier(
    device=device,
    batch_size=1  # Небольшой размер пакета для улучшенной точности
)

preprocessing = AutoScene(scene_classifier=scene_classifier)

postprocessing = CasMattingMethod(
    refining_module=cascade_psp,
    matting_module=fba,
    trimap_generator=trimap,
    device=device
)

interface = Interface(pre_pipe=preprocessing, post_pipe=postprocessing, seg_pipe=seg_net)

images_without_background = interface(['/Users/petrkulikov/spare_parts/201-2102-2454.JPG'])

picture_without_background = images_without_background[0]
picture_without_background.save("sample22.png")
