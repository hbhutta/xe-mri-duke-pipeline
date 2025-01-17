function resize_img(nifti_path)
    disp("Resizing...");
    disp(nifti_path);
    scale_factor = 2;

    %  Originally scale_nifti function, put in here instead to have one function per file
    disp("Scaling NIFTI file");
    r = niftiread(nifti_path);
    r_s = imresize3(r, scale_factor);
    [path, name, ~] = fileparts(nifti_path);
    save_path = fullfile(path, strcat(name, "_scaled.nii"));
    disp(save_path);
    niftiwrite(r_s, save_path);
end