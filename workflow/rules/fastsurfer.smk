

def get_transform_filename(wildcards):
    file=[]
    if config['contrast_t1']['present'] and config['noncontrast_t1']['present']:
        file=expand(bids(root=join(config['out_dir'], 'derivatives', 'atlasreg'),subject=config['subject_prefix']+'{subject}',suffix='xfm.txt',from_='noncontrast',to='contrast',desc='rigid',type_='ras'),subject=wildcards.subject),
    if len(file) >0:
        file=file[0][0]
    print(file)
    return file

if config['fastsurfer']['version'] =='dev':
    rule fastsurfer_seg:
        input: 
            t1 = get_noncontrast_filename_fs(expand(subject_id,subject=subjects),config['fastsurfer']['ses']),
        params:
            fastsurfer_run = config['fastsurfer']['home'],
            sid = config['fastsurfer']['sid'],
            batch = config['fastsurfer']['batch'],
            threads = config['fastsurfer']['threads'],
            vox_size = config['fastsurfer']['vox_size'],
            py = config['fastsurfer']['py'],
            fastsurfer_out = directory(join(config['out_dir'], 'derivatives', 'fastsurfer')),
            subjid=expand('sub-' + subject_id,subject=subjects),
        output:
            touch_fastsurfer=touch(join(config['out_dir'], 'logs', 'sub-' + subject_id + "_fastsurfer.done")),
            t1_fname = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'mri','orig.mgz'),
        #threads:config['fastsurfer']['threads']
        group: 'preproc'
        threads: 1
        shell:
            "export FASTSURFER_HOME={params.fastsurfer_run} &&PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:4096 {params.fastsurfer_run}/run_fastsurfer.sh \
            --t1 {input.t1} --sd {params.fastsurfer_out} --threads {params.threads} --vox_size {params.vox_size} --sid {params.subjid} --py {params.py} --viewagg_device cpu --fsaparc --parallel --allow_root"
elif config['fastsurfer']['version'] =='stable':
    rule fastsurfer_seg:
        input: 
            t1 = get_noncontrast_filename_fs(expand(subject_id,subject=subjects),config['fastsurfer']['ses']),
        params:
            fastsurfer_run = config['fastsurfer']['home'],
            sid = config['fastsurfer']['sid'],
            batch = config['fastsurfer']['batch'],
            threads = config['fastsurfer']['threads'],
            vox_size = config['fastsurfer']['vox_size'],
            py = config['fastsurfer']['py'],
            fastsurfer_out = directory(join(config['out_dir'], 'derivatives', 'fastsurfer')),
            subjid=expand('sub-' + subject_id,subject=subjects),
        output:
            touch_fastsurfer=touch(join(config['out_dir'], 'logs', 'sub-' + subject_id + "_fastsurfer.done")),
            t1_fname = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'mri','orig.mgz'),
        #threads:config['fastsurfer']['threads']
        group: 'preproc'
        threads: 1
        shell:
            "export FASTSURFER_HOME={params.fastsurfer_run} &&PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:4096 {params.fastsurfer_run}/run_fastsurfer.sh \
            --t1 {input.t1} --sd {params.fastsurfer_out} --sid {params.subjid} --py {params.py} --vox_size {params.vox_size} --viewagg_device cpu --fsaparc --no_cereb --parallel --ignore_fs_version --allow_root"
elif config['fastsurfer']['version'] =='master':
    rule fastsurfer_seg:
        input: 
            t1 = get_noncontrast_filename_fs(expand(subject_id,subject=subjects),config['fastsurfer']['ses']),
        params:
            fastsurfer_run = config['fastsurfer']['home'],
            sid = config['fastsurfer']['sid'],
            batch = config['fastsurfer']['batch'],
            threads = config['fastsurfer']['threads'],
            py = config['fastsurfer']['py'],
            fastsurfer_out = directory(join(config['out_dir'], 'derivatives', 'fastsurfer')),
            subjid=expand('sub-' + subject_id,subject=subjects),
        output:
            touch_fastsurfer=touch(join(config['out_dir'], 'logs', 'sub-' + subject_id + "_fastsurfer.done")),
            t1_fname = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'mri','orig.mgz'),
        #threads:config['fastsurfer']['threads']
        group: 'preproc'
        threads: 1
        shell:
            "export FASTSURFER_HOME={params.fastsurfer_run} &&PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:4096 {params.fastsurfer_run}/run_fastsurfer.sh \
            --t1 {input.t1} --sd {params.fastsurfer_out} --sid {params.subjid} --py {params.py} --run_viewagg_on cpu --fsaparc --parallel"

final_outputs.extend(expand(rules.fastsurfer_seg.output.touch_fastsurfer, subject=subjects))

rule fastsurfer_symlinks:
    input: 
        t1_fname = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'mri','orig.mgz'),
    params:
        talairach_xfm = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'mri','transforms','talairach.xfm.lta'),
        lh_pial_t1 = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'surf','lh.pial.T1'),
        rh_pial_t1 = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'surf','rh.pial.T1'),
        lh_white_preaparc_h = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'surf','lh.white.preaparc.H'),
        rh_white_preaparc_h = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'surf','rh.white.preaparc.H'),
        lh_white_preaparc_k = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'surf','lh.white.preaparc.K'),
        rh_white_preaparc_k = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'surf','lh.white.preaparc.K'),
    output:
        talairach_lta = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'mri','transforms','talairach.lta'),
        talairach_skull_lta = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'mri','transforms','talairach_with_skull.lta'),
        rawavg = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'mri','rawavg.mgz'),
        lh_pial = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'surf','lh.pial'),
        rh_pial = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'surf','rh.pial'),
        lh_white_h = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'surf','lh.white.H'),
        rh_white_h = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'surf','rh.white.H'),
        lh_white_k = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'surf','lh.white.K'),
        rh_white_k = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'surf','rh.white.K'),
    group: 'preproc'
    threads: 1
    shell:
        "cp {params.talairach_xfm} {output.talairach_lta}&&\
        cp {params.talairach_xfm} {output.talairach_skull_lta}&&\
        cp {input.t1_fname} {output.rawavg}&&\
        cp {params.lh_pial_t1} {output.lh_pial}&&\
        cp {params.rh_pial_t1} {output.rh_pial}&&\
        cp {params.lh_white_preaparc_h} {output.lh_white_h}&&\
        cp {params.rh_white_preaparc_h} {output.rh_white_h}&&\
        cp {params.lh_white_preaparc_k} {output.lh_white_k}&&\
        cp {params.rh_white_preaparc_k} {output.rh_white_k}"

final_outputs.extend(expand(rules.fastsurfer_symlinks.output.rh_white_k, subject=subjects))

if config['seeg_contacts']['present']:
    rule vis_electrodes_native:
        input: 
            fcsv = get_electrodes_coords(expand(subject_id,subject=subjects),coords_space='native',coords_type='SEEGA'),
            t1_fname = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'mri','orig.mgz'),
            xfm_noncontrast = get_transform_filename,
        params:
            lh_pial = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'surf','lh.pial'),
            rh_pial = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'surf','rh.pial'),
            lh_sulc = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'surf','lh.sulc'),
            rh_sulc = join(config['out_dir'],'derivatives','fastsurfer','sub-' + subject_id, 'surf','rh.sulc'),
        output:
            html = report(bids(root=join(config['out_dir'], 'derivatives', 'atlasreg'),prefix='sub-'+subject_id+'/qc/sub-'+subject_id,suffix='electrodes.html',space='native'),
                    caption='../reports/electrodes_vis.rst',
                    category='Electrodes in template space',
                    subcategory='{desc} reg to {template}'),
        group: 'preproc'
        threads: 1
        script: '../scripts/vis_electrodes_native.py'

    final_outputs.extend(expand(bids(root=join(config['out_dir'], 'derivatives', 'atlasreg'),prefix='sub-'+subject_id+'/qc/sub-'+subject_id,suffix='electrodes.html',space='native',include_subject_dir=False),
                        subject=subjects))
