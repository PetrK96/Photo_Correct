import PIL.Image
from carvekit.api.interface import Interface
from carvekit.ml.wrap.fba_matting import FBAMatting
from carvekit.ml.wrap.scene_classifier import SceneClassifier
from carvekit.ml.wrap.cascadepsp import CascadePSP
from carvekit.ml.wrap.tracer_b7 import TracerUniversalB7
from carvekit.pipelines.postprocessing import CasMattingMethod
from carvekit.pipelines.preprocessing import AutoScene
from carvekit.trimap.generator import TrimapGenerator


seg_net = TracerUniversalB7(device='cpu', batch_size=4, fp16=False)
cascade_psp = CascadePSP(device='cpu', batch_size=1, input_tensor_size=900, fp16=False, processing_accelerate_image_size=1024, global_step_only=False)
fba = FBAMatting(device='cpu', input_tensor_size=1024, batch_size=5, fp16=False)
trimap = TrimapGenerator(filter_threshold=-1, prob_threshold=231, kernel_size=30, erosion_iters=6)
scene_classifier = SceneClassifier(device='cpu', batch_size=3)
preprocessing = AutoScene(scene_classifier=scene_classifier)
postprocessing = CasMattingMethod(refining_module=cascade_psp, matting_module=fba, trimap_generator=trimap, device='cpu')

interface = Interface(pre_pipe=preprocessing, post_pipe=postprocessing, seg_pipe=seg_net)

images_without_background = interface(['/Users/petrkulikov/spare_parts/201-2102-2454.JPG'])

picture_without_background = images_without_background[0]
picture_without_background.save("sample22.png")
